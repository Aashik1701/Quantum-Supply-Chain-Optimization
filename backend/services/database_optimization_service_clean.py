"""
Database-enabled optimization service with persistent job tracking
"""
import uuid
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from contextlib import contextmanager

from config.database import get_db_session
from models.database import (
    OptimizationJob, OptimizationResult, JobStatus, OptimizationMethod
)
from repositories.database import (
    OptimizationJobRepository, OptimizationResultRepository
)
from classical.linear_programming import LinearProgrammingSolver
from quantum.qaoa_solver import QAOASolver
from utils.exceptions import OptimizationError


logger = logging.getLogger(__name__)


class DatabaseOptimizationService:
    """Optimization service with database persistence"""

    def __init__(self):
        """Initialize optimization service"""
        self.lp_solver = LinearProgrammingSolver()
        self.qaoa_solver = QAOASolver()

    @contextmanager
    def _get_session(self):
        """Get database session with automatic cleanup"""
        session = get_db_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

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
                parameters=data,
                status=JobStatus.RUNNING
            )

            try:
                # Run optimization
                result_data = self.lp_solver.solve(data)

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
                parameters=data,
                status=JobStatus.RUNNING
            )

            try:
                # Run optimization
                result_data = self.qaoa_solver.solve(data)

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
                parameters=data,
                status=JobStatus.RUNNING
            )

            try:
                # Run both classical and quantum, compare results
                classical_result = self.lp_solver.solve(data)
                quantum_result = self.qaoa_solver.solve(data)

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
                    execution_time=best_result.get('execution_time', 0.0)
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
                    'execution_time': result.execution_time,
                    'created_at': result.created_at.isoformat(),
                    'result_data': result.result_data
                }
                for result in results
            ]
