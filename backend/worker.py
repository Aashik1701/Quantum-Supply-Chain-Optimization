"""
RQ worker task definitions for background optimization jobs.
Requires REDIS_URL environment variable to be set for cross-process communication.
"""
import os
import logging
from typing import Dict, Any, Optional

from config.database import get_db
from repositories.database import (
    OptimizationJobRepository, OptimizationResultRepository
)
from models.database import JobStatus, OptimizationMethod
from utils.exceptions import OptimizationError

logger = logging.getLogger(__name__)


def _get_services():
    """Helper to instantiate services inside worker process."""
    session = next(get_db())
    job_repo = OptimizationJobRepository(session)
    result_repo = OptimizationResultRepository(session)
    return session, job_repo, result_repo


def process_quantum_job(
    job_id: str,
    data: Dict[str, Any],
    backend_policy: str = 'simulator',
    backend_name: Optional[str] = None,
):
    """Background task: run quantum optimization and persist results.

    Emits progress to SocketIO via Redis message queue if configured.
    """
    session, job_repo, result_repo = _get_services()
    try:
        # Update status to running
        job_repo.update_status(job_id, JobStatus.RUNNING)

        # Select backend and set up optimizer with progress callback
        from config.quantum_config import ibm_quantum
        from quantum.qaoa_solver import QuantumOptimizer

        selected_backend = None
        use_ibm = False
        if backend_name or backend_policy != 'simulator':
            selected_backend = ibm_quantum.select_backend(backend_policy, backend_name)
            use_ibm = bool(selected_backend)

        # Progress emitter via SocketIO message queue
        def progress_callback(progress_data):
            try:
                from flask_socketio import SocketIO
                redis_url = os.environ.get('REDIS_URL')
                if not redis_url:
                    return
                socketio = SocketIO(message_queue=redis_url)
                socketio.emit(
                    'optimization_progress',
                    {
                        'job_id': job_id,
                        'iteration': progress_data['iteration'],
                        'energy': progress_data['energy'],
                        'timestamp': progress_data['timestamp'],
                    },
                    room=job_id,
                )
            except Exception as e:
                logger.warning(f"Worker progress emit failed: {e}")

        optimizer = QuantumOptimizer(
            backend=selected_backend if (use_ibm and selected_backend) else 'qasm_simulator',
            use_ibm=use_ibm,
            progress_callback=progress_callback,
        )

        warehouses = data.get('warehouses', [])
        customers = data.get('customers', [])
        import numpy as np
        # Simple Euclidean distance matrix (mirror the service implementation)
        n_w, n_c = len(warehouses), len(customers)
        distance_matrix = np.zeros((n_w, n_c))
        for i, w in enumerate(warehouses):
            for j, c in enumerate(customers):
                distance_matrix[i, j] = ((c['latitude'] - w['latitude'])**2 + (c['longitude'] - w['longitude'])**2) ** 0.5

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

        # Persist result
        result_repo.create(
            job_id=job_id,
            result_data=result_data,
            total_cost=result_data.get('total_cost', 0.0),
            execution_time=result_data.get('optimization_time', 0.0),
        )

        job_repo.update_status(job_id, JobStatus.COMPLETED)

        # Emit completion
        try:
            from flask_socketio import SocketIO
            redis_url = os.environ.get('REDIS_URL')
            if redis_url:
                socketio = SocketIO(message_queue=redis_url)
                socketio.emit('optimization_complete', {'job_id': job_id}, room=job_id)
        except Exception:
            pass

        return {'job_id': job_id, 'status': 'completed'}

    except Exception as e:
        job_repo.update_status(job_id, JobStatus.FAILED, error_message=str(e))
        try:
            from flask_socketio import SocketIO
            redis_url = os.environ.get('REDIS_URL')
            if redis_url:
                socketio = SocketIO(message_queue=redis_url)
                socketio.emit('optimization_error', {'job_id': job_id, 'error': str(e)}, room=job_id)
        except Exception:
            pass
        raise OptimizationError(f"Worker quantum job failed: {e}")
    finally:
        session.close()
