"""
Database-enabled optimization service with persistent job tracking
"""
import uuid
import logging
import numpy as np
import subprocess
import json
import os
from typing import Dict, Any, List
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

    def __init__(self):
        """Initialize optimization service"""
        self.lp_solver = ClassicalOptimizer()
        self.qaoa_solver = QuantumOptimizer()

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
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run quantum optimization with database job tracking
        """
        with self._get_session() as session:
            job_repo = OptimizationJobRepository(session)
            result_repo = OptimizationResultRepository(session)

            # Create optimization job
            job = job_repo.create(
                method=OptimizationMethod.QUANTUM,
                input_data=data,
                parameters=data
            )
            
            # Update status to running
            job_repo.update_status(job.id, JobStatus.RUNNING)

            try:
                # Run optimization
                warehouses = data.get('warehouses', [])
                customers = data.get('customers', [])
                distance_matrix = self._calculate_distance_matrix(
                    warehouses, customers
                )
                result_data = self.qaoa_solver.optimize(
                    warehouses=warehouses,
                    customers=customers,
                    distance_matrix=distance_matrix,
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

                status = {
                    'job_id': str(job.id),
                    'status': job.status.value,
                    'method': job.method.value,
                    'created_at': job.created_at.isoformat(),
                    'updated_at': job.updated_at.isoformat()
                }

                if job.error_message:
                    status['error'] = job.error_message

                # Get result if completed
                if job.status == JobStatus.COMPLETED:
                    result_repo = OptimizationResultRepository(session)
                    result = result_repo.get_by_job_id(job.id)
                    if result:
                        status['result'] = result.result_data
                        status['total_cost'] = result.total_cost
                        status['execution_time'] = result.execution_time

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
