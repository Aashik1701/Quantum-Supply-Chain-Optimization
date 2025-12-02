"""
Database-enabled optimization service with persistent job tracking
"""
import uuid
import logging
import numpy as np
import subprocess
import json
import os
from typing import Dict, Any, List, Optional
from contextlib import contextmanager

from config.database import get_db
from models.database import (
    JobStatus, OptimizationMethod
)
from repositories.database import (
    OptimizationJobRepository, OptimizationResultRepository
)
from classical.linear_programming import ClassicalOptimizer
from quantum.qaoa_solver import QuantumOptimizer
from utils.exceptions import OptimizationError


logger = logging.getLogger(__name__)


class DatabaseOptimizationService:
    """Optimization service with database persistence"""

    def __init__(self, socketio=None):
        """Initialize optimization service
        
        Args:
            socketio: Flask-SocketIO instance for progress streaming
        """
        self.lp_solver = ClassicalOptimizer()
        self.qaoa_solver = QuantumOptimizer()
        self.socketio = socketio
        # Lazy import to avoid hard dependency if not using batch mode
        self._rq_queue = None
        self._redis_url = os.environ.get('REDIS_URL')

    def _get_rq_queue(self):
        """Get or create RQ queue instance"""
        if self._rq_queue is None:
            try:
                from rq import Queue
                from redis import Redis
                redis_conn = Redis.from_url(self._redis_url) if self._redis_url else Redis()
                self._rq_queue = Queue('optimization', connection=redis_conn)
            except Exception as e:
                logger.warning(f"RQ not available: {e}")
                self._rq_queue = None
        return self._rq_queue

    def enqueue_quantum_job(
        self,
        data: Dict[str, Any],
        backend_policy: str = 'simulator',
        backend_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Enqueue quantum optimization job to background worker.

        Returns a payload with the job id for client to track.
        """
        with self._get_session() as session:
            job_repo = OptimizationJobRepository(session)

            # Create job as pending
            job = job_repo.create(
                method=OptimizationMethod.QUANTUM,
                input_data=data,
                parameters={**data, 'backendPolicy': backend_policy, 'backendName': backend_name}
            )

            # Enqueue RQ task
            queue = self._get_rq_queue()
            if not queue:
                raise OptimizationError('Background queue not available')

            from worker import process_quantum_job
            rq_job = queue.enqueue(
                process_quantum_job,
                str(job.id),
                data,
                backend_policy,
                backend_name,
                job_timeout=60 * 30,
            )

            # Update to running (worker will update further)
            job_repo.update_status(job.id, JobStatus.RUNNING)

            return {
                'job_id': str(job.id),
                'rq_id': rq_job.id,
                'status': 'enqueued'
            }

    @contextmanager
    def _get_session(self):
        """Get database session with automatic cleanup"""
        session = next(get_db())
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def _calculate_distance_matrix(
        self,
        warehouses: List[Dict],
        customers: List[Dict]
    ) -> np.ndarray:
        """Calculate distance matrix between warehouses and customers"""
        n_warehouses = len(warehouses)
        n_customers = len(customers)
        distance_matrix = np.zeros((n_warehouses, n_customers))
        
        for i, warehouse in enumerate(warehouses):
            for j, customer in enumerate(customers):
                # Simple Euclidean distance calculation
                lat1, lon1 = warehouse['latitude'], warehouse['longitude']
                lat2, lon2 = customer['latitude'], customer['longitude']
                distance = np.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)
                distance_matrix[i, j] = distance
        
        return distance_matrix

    def run_classical_optimization(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run classical optimization with database job tracking
        """
        with self._get_session() as session:
            job_repo = OptimizationJobRepository(session)
            result_repo = OptimizationResultRepository(session)

            # Create optimization job
            job = job_repo.create(
                method=OptimizationMethod.CLASSICAL,
                input_data=data,
                parameters=data
            )
            
            # Update status to running
            job_repo.update_status(job.id, JobStatus.RUNNING)

            try:
                # Extract data and calculate distance matrix
                warehouses = data.get('warehouses', [])
                customers = data.get('customers', [])
                
                # Calculate distance matrix (simple Euclidean distance)
                distance_matrix = self._calculate_distance_matrix(
                    warehouses, customers
                )
                
                # Run optimization
                result_data = self.lp_solver.optimize(
                    warehouses=warehouses,
                    customers=customers,
                    distance_matrix=distance_matrix
                )

                # Create result record
                result_repo.create(
                    job_id=job.id,
                    result_data=result_data,
                    total_cost=result_data.get('total_cost', 0.0),
                    execution_time=result_data.get('execution_time', 0.0)
                )

                # Update job status
                job_repo.update_status(job.id, JobStatus.COMPLETED)

                return {
                    'job_id': str(job.id),
                    'status': 'completed',
                    'result': result_data,
                    'method': 'classical'
                }

            except Exception as e:
                # Update job status to failed
                job_repo.update_status(
                    job.id,
                    JobStatus.FAILED,
                    error_message=str(e)
                )
                raise OptimizationError(
                    f"Classical optimization failed: {str(e)}"
                )

    def run_quantum_optimization(
        self,
        data: Dict[str, Any],
        backend_policy: str = 'simulator',
        backend_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run quantum optimization with database job tracking
        
        Args:
            data: Optimization input data
            backend_policy: 'simulator', 'device', or 'shortest_queue'
            backend_name: Optional specific backend name
        """
        with self._get_session() as session:
            job_repo = OptimizationJobRepository(session)
            result_repo = OptimizationResultRepository(session)

            # Create optimization job
            job = job_repo.create(
                method=OptimizationMethod.QUANTUM,
                input_data=data,
                parameters={**data, 'backendPolicy': backend_policy, 'backendName': backend_name}
            )
            
            # Update status to running
            job_repo.update_status(job.id, JobStatus.RUNNING)

            try:
                # Select backend based on policy
                from config.quantum_config import ibm_quantum
                selected_backend = None
                use_ibm = False
                
                if backend_name or backend_policy != 'simulator':
                    # Try to use IBM backend
                    selected_backend = ibm_quantum.select_backend(backend_policy, backend_name)
                    use_ibm = bool(selected_backend)
                
                # Run optimization
                warehouses = data.get('warehouses', [])
                customers = data.get('customers', [])
                distance_matrix = self._calculate_distance_matrix(
                    warehouses, customers
                )
                
                # Create progress callback for WebSocket streaming
                def progress_callback(progress_data):
                    if self.socketio:
                        try:
                            self.socketio.emit(
                                'optimization_progress',
                                {
                                    'job_id': str(job.id),
                                    'iteration': progress_data['iteration'],
                                    'energy': progress_data['energy'],
                                    'timestamp': progress_data['timestamp']
                                },
                                room=str(job.id)
                            )
                        except Exception as e:
                            logger.warning(f"Failed to emit progress: {e}")
                
                # Create optimizer with selected backend
                from quantum.qaoa_solver import QuantumOptimizer
                if use_ibm and selected_backend:
                    optimizer = QuantumOptimizer(
                        backend=selected_backend, 
                        use_ibm=True,
                        progress_callback=progress_callback
                    )
                else:
                    optimizer = QuantumOptimizer(
                        backend='qasm_simulator', 
                        use_ibm=False,
                        progress_callback=progress_callback
                    )
                
                # Extract reduction and warm-start parameters
                enable_reduction = data.get('enable_reduction', data.get('enableReduction', False))
                max_customers = data.get('max_customers', data.get('maxCustomers', 50))
                warm_start = data.get('warm_start', data.get('warmStart', False))
                classical_solution = data.get('classical_solution', data.get('classicalSolution', {}))
                
                result_data = optimizer.optimize(
                    warehouses=warehouses,
                    customers=customers,
                    distance_matrix=distance_matrix,
                    enable_reduction=enable_reduction,
                    max_customers=max_customers,
                    warm_start=warm_start,
                    classical_solution=classical_solution,
                )

                # Create result record
                result_repo.create(
                    job_id=job.id,
                    result_data=result_data,
                    total_cost=result_data.get('total_cost', 0.0),
                    execution_time=result_data.get('optimization_time', 0.0),
                )

                # Update job status
                job_repo.update_status(job.id, JobStatus.COMPLETED)

                return {
                    'job_id': str(job.id),
                    'status': 'completed',
                    'result': result_data,
                    'method': 'quantum'
                }

            except Exception as e:
                # Update job status to failed
                job_repo.update_status(
                    job.id,
                    JobStatus.FAILED,
                    error_message=str(e)
                )
                raise OptimizationError(
                    f"Quantum optimization failed: {str(e)}"
                )

    def run_vrp_optimization(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run VRP (Vehicle Routing Problem) optimization
        """
        with self._get_session() as session:
            job_repo = OptimizationJobRepository(session)
            result_repo = OptimizationResultRepository(session)

            # Create optimization job
            job = job_repo.create(
                method=OptimizationMethod.CLASSICAL,
                input_data=data,
                parameters=data
            )
            
            # Update status to running
            job_repo.update_status(job.id, JobStatus.RUNNING)

            try:
                # Run VRP classical optimization
                import sys
                import importlib.util
                
                # Import the classical VRP module
                vrp_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    'quantum', 'classical_vrp_export.py'
                )
                
                spec = importlib.util.spec_from_file_location(
                    "classical_vrp_export", vrp_path
                )
                vrp_module = importlib.util.module_from_spec(spec)
                sys.modules["classical_vrp_export"] = vrp_module
                spec.loader.exec_module(vrp_module)
                
                # Execute VRP and get results
                baseline_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    'outputs', 'baseline.json'
                )
                
                # If baseline.json exists, load it
                vrp_result = None
                if os.path.exists(baseline_path):
                    with open(baseline_path, 'r') as f:
                        vrp_result = json.load(f)
                
                if not vrp_result:
                    # Run VRP if no cached result
                    # Execute as subprocess to avoid variable scope issues
                    result = subprocess.run([
                        'python3', vrp_path
                    ], cwd=os.path.dirname(vrp_path),
                       capture_output=True, text=True)
                    
                    if result.returncode != 0:
                        raise OptimizationError(
                            f"VRP execution failed: {result.stderr}"
                        )
                    
                    if os.path.exists(baseline_path):
                        with open(baseline_path, 'r') as f:
                            vrp_result = json.load(f)
                
                if not vrp_result:
                    raise OptimizationError(
                        "VRP optimization failed to produce results"
                    )
                
                # Format result for database
                result_data = {
                    'total_cost': vrp_result.get('total_distance', 0),
                    'total_distance': vrp_result.get('total_distance', 0),
                    'total_load': vrp_result.get('total_load', 0),
                    'routes': vrp_result.get('routes', []),
                    'num_vehicles_used': len(vrp_result.get('routes', [])),
                    'optimization_time': 1.0,
                    'method': 'vrp_classical'
                }

                # Create result record
                result_repo.create(
                    job_id=job.id,
                    result_data=result_data,
                    total_cost=result_data.get('total_cost', 0.0),
                    execution_time=result_data.get('optimization_time', 0.0)
                )

                # Update job status
                job_repo.update_status(job.id, JobStatus.COMPLETED)

                return {
                    'job_id': str(job.id),
                    'status': 'completed',
                    'result': result_data,
                    'method': 'vrp'
                }

            except Exception as e:
                # Update job status to failed
                job_repo.update_status(
                    job.id,
                    JobStatus.FAILED,
                    error_message=str(e)
                )
                raise OptimizationError(
                    f"VRP optimization failed: {str(e)}"
                )

    def run_hybrid_vrp_optimization(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run hybrid VRP optimization (classical + quantum enhancement)
        """
        with self._get_session() as session:
            job_repo = OptimizationJobRepository(session)
            result_repo = OptimizationResultRepository(session)

            # Create optimization job
            job = job_repo.create(
                method=OptimizationMethod.HYBRID,
                input_data=data,
                parameters=data
            )
            
            # Update status to running
            job_repo.update_status(job.id, JobStatus.RUNNING)

            try:
                # Run hybrid integration
                import sys
                import importlib.util
                
                # First run classical VRP
                vrp_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    'quantum', 'classical_vrp_export.py'
                )
                
                spec = importlib.util.spec_from_file_location(
                    "classical_vrp_export", vrp_path
                )
                vrp_module = importlib.util.module_from_spec(spec)
                sys.modules["classical_vrp_export"] = vrp_module
                spec.loader.exec_module(vrp_module)
                
                # Then run hybrid integration
                hybrid_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    'quantum', 'hybrid_integration.py'
                )
                
                spec = importlib.util.spec_from_file_location(
                    "hybrid_integration", hybrid_path
                )
                hybrid_module = importlib.util.module_from_spec(spec)
                sys.modules["hybrid_integration"] = hybrid_module
                spec.loader.exec_module(hybrid_module)
                
                # Execute hybrid optimization
                hybrid_result = hybrid_module.main()
                
                if not hybrid_result:
                    raise OptimizationError(
                        "Hybrid optimization failed to produce results"
                    )
                
                # Format result for database
                result_data = {
                    'total_cost': hybrid_result.get('total_distance', 0),
                    'total_distance': hybrid_result.get('total_distance', 0),
                    'total_load': hybrid_result.get('total_load', 0),
                    'routes': hybrid_result.get('vehicles', []),
                    'num_vehicles_used': len(
                        hybrid_result.get('vehicles', [])
                    ),
                    'optimization_time': 2.0,
                    'method': 'hybrid_vrp'
                }

                # Create result record
                result_repo.create(
                    job_id=job.id,
                    result_data=result_data,
                    total_cost=result_data.get('total_cost', 0.0),
                    execution_time=result_data.get('optimization_time', 0.0)
                )

                # Update job status
                job_repo.update_status(job.id, JobStatus.COMPLETED)

                return {
                    'job_id': str(job.id),
                    'status': 'completed',
                    'result': result_data,
                    'method': 'hybrid_vrp'
                }

            except Exception as e:
                # Update job status to failed
                job_repo.update_status(
                    job.id,
                    JobStatus.FAILED,
                    error_message=str(e)
                )
                raise OptimizationError(
                    f"Hybrid VRP optimization failed: {str(e)}"
                )

    def run_hybrid_optimization(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run hybrid optimization with database job tracking
        """
        with self._get_session() as session:
            job_repo = OptimizationJobRepository(session)
            result_repo = OptimizationResultRepository(session)

            # Create optimization job
            job = job_repo.create(
                method=OptimizationMethod.HYBRID,
                input_data=data,
                parameters=data
            )
            
            # Update status to running
            job_repo.update_status(job.id, JobStatus.RUNNING)

            try:
                # Run both classical and quantum, compare results
                warehouses = data.get('warehouses', [])
                customers = data.get('customers', [])
                distance_matrix = self._calculate_distance_matrix(
                    warehouses, customers
                )
                classical_result = self.lp_solver.optimize(
                    warehouses=warehouses,
                    customers=customers,
                    distance_matrix=distance_matrix,
                )
                quantum_result = self.qaoa_solver.optimize(
                    warehouses=warehouses,
                    customers=customers,
                    distance_matrix=distance_matrix,
                )

                # Select best result based on cost
                classical_cost = classical_result.get(
                    'total_cost', float('inf')
                )
                quantum_cost = quantum_result.get('total_cost', float('inf'))

                if classical_cost <= quantum_cost:
                    best_result = classical_result
                    best_result['selected_method'] = 'classical'
                else:
                    best_result = quantum_result
                    best_result['selected_method'] = 'quantum'

                best_result['classical_cost'] = classical_cost
                best_result['quantum_cost'] = quantum_cost

                # Create result record
                result_repo.create(
                    job_id=job.id,
                    result_data=best_result,
                    total_cost=best_result.get('total_cost', 0.0),
                    execution_time=best_result.get('optimization_time', 0.0),
                )

                # Update job status
                job_repo.update_status(job.id, JobStatus.COMPLETED)

                return {
                    'job_id': str(job.id),
                    'status': 'completed',
                    'result': best_result,
                    'method': 'hybrid'
                }

            except Exception as e:
                # Update job status to failed
                job_repo.update_status(
                    job.id,
                    JobStatus.FAILED,
                    error_message=str(e)
                )
                raise OptimizationError(
                    f"Hybrid optimization failed: {str(e)}"
                )

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get optimization job status"""
        with self._get_session() as session:
            job_repo = OptimizationJobRepository(session)
            
            try:
                job_uuid = uuid.UUID(job_id)
                job = job_repo.get_by_id(job_uuid)
                
                if not job:
                    raise OptimizationError(f"Job {job_id} not found")

                last_update = job.completed_at or job.started_at or job.created_at
                status = {
                    'job_id': str(job.id),
                    'status': job.status.value,
                    'method': job.method.value,
                    'created_at': job.created_at.isoformat(),
                    'updated_at': last_update.isoformat() if last_update else None,
                }

                if job.error_message:
                    status['error'] = job.error_message

                # Get result if completed
                if job.status == JobStatus.COMPLETED:
                    result_repo = OptimizationResultRepository(session)
                    result = result_repo.get_by_job_id(job.id)
                    if result:
                        status['result'] = {
                            'routes': result.routes_data,
                            'assignments': result.assignments_data,
                            'performanceMetrics': result.performance_metrics,
                        }
                        status['total_cost'] = result.total_cost
                        status['execution_time'] = result.optimization_time

                return status

            except ValueError:
                raise OptimizationError(f"Invalid job ID format: {job_id}")

    def get_job_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent optimization jobs"""
        with self._get_session() as session:
            job_repo = OptimizationJobRepository(session)
            jobs = job_repo.get_recent(limit)
            
            return [
                {
                    'job_id': str(job.id),
                    'status': job.status.value,
                    'method': job.method.value,
                    'created_at': job.created_at.isoformat(),
                    'updated_at': job.updated_at.isoformat()
                }
                for job in jobs
            ]

    def get_recent_results(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent optimization results"""
        with self._get_session() as session:
            result_repo = OptimizationResultRepository(session)
            results = result_repo.get_recent(limit)
            
            return [
                {
                    'job_id': str(result.job_id),
                    'total_cost': result.total_cost,
                    'execution_time': result.optimization_time,
                    'created_at': result.created_at.isoformat(),
                    'result_data': result.routes_data
                }
                for result in results
            ]
