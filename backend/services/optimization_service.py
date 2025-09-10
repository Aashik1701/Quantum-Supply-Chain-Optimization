"""
Optimization service orchestrator
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import asyncio
import json

from classical.linear_programming import ClassicalOptimizer
from quantum.qaoa_solver import QuantumOptimizer
from utils.helpers import calculate_distance_matrix, format_optimization_result


class OptimizationService:
    """Service for orchestrating optimization workflows"""
    
    def __init__(self):
        self.classical_optimizer = ClassicalOptimizer()
        self.quantum_optimizer = QuantumOptimizer()
        self.job_store = {}  # In production, use Redis
        self.results_store = {}  # In production, use database
    
    def run_classical_optimization(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run classical optimization algorithm"""
        job_id = str(uuid.uuid4())
        
        try:
            # Create job record
            self.job_store[job_id] = {
                'id': job_id,
                'method': 'classical',
                'status': 'running',
                'created_at': datetime.utcnow().isoformat(),
                'progress': 0
            }
            
            # Extract data
            warehouses = data.get('warehouses', [])
            customers = data.get('customers', [])
            
            # Calculate distance matrix
            distance_matrix = calculate_distance_matrix(warehouses, customers)
            
            # Run optimization
            result = self.classical_optimizer.optimize(
                warehouses=warehouses,
                customers=customers,
                distance_matrix=distance_matrix
            )
            
            # Format and store result
            formatted_result = format_optimization_result(result, 'classical')
            self.results_store[job_id] = formatted_result
            
            # Update job status
            self.job_store[job_id]['status'] = 'completed'
            self.job_store[job_id]['progress'] = 100
            
            return formatted_result
            
        except Exception as e:
            self.job_store[job_id]['status'] = 'failed'
            self.job_store[job_id]['error'] = str(e)
            raise e
    
    def run_quantum_optimization(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run quantum optimization algorithm (QAOA)"""
        job_id = str(uuid.uuid4())
        
        try:
            # Create job record
            self.job_store[job_id] = {
                'id': job_id,
                'method': 'quantum',
                'status': 'running',
                'created_at': datetime.utcnow().isoformat(),
                'progress': 0
            }
            
            # Extract data
            warehouses = data.get('warehouses', [])
            customers = data.get('customers', [])
            quantum_params = data.get('quantum_params', {})
            
            # Calculate distance matrix
            distance_matrix = calculate_distance_matrix(warehouses, customers)
            
            # Run optimization
            result = self.quantum_optimizer.optimize(
                warehouses=warehouses,
                customers=customers,
                distance_matrix=distance_matrix,
                **quantum_params
            )
            
            # Format and store result
            formatted_result = format_optimization_result(result, 'quantum')
            self.results_store[job_id] = formatted_result
            
            # Update job status
            self.job_store[job_id]['status'] = 'completed'
            self.job_store[job_id]['progress'] = 100
            
            return formatted_result
            
        except Exception as e:
            self.job_store[job_id]['status'] = 'failed'
            self.job_store[job_id]['error'] = str(e)
            raise e
    
    def run_hybrid_optimization(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run hybrid quantum-classical optimization"""
        job_id = str(uuid.uuid4())
        
        try:
            # Create job record
            self.job_store[job_id] = {
                'id': job_id,
                'method': 'hybrid',
                'status': 'running',
                'created_at': datetime.utcnow().isoformat(),
                'progress': 0
            }
            
            # Step 1: Classical preprocessing (50% progress)
            classical_result = self.run_classical_optimization(data)
            self.job_store[job_id]['progress'] = 50
            
            # Step 2: Quantum refinement (100% progress)
            # Use classical result as initial solution for quantum optimization
            quantum_data = data.copy()
            quantum_data['initial_solution'] = classical_result.get('routes', [])
            
            quantum_result = self.run_quantum_optimization(quantum_data)
            self.job_store[job_id]['progress'] = 100
            
            # Combine results (choose better one)
            if quantum_result['total_cost'] < classical_result['total_cost']:
                final_result = quantum_result
                final_result['method'] = 'hybrid'
                final_result['improvement_over_classical'] = {
                    'cost_reduction': (classical_result['total_cost'] - quantum_result['total_cost']) / classical_result['total_cost'] * 100,
                    'co2_reduction': (classical_result['total_co2'] - quantum_result['total_co2']) / classical_result['total_co2'] * 100
                }
            else:
                final_result = classical_result
                final_result['method'] = 'hybrid'
                final_result['note'] = 'Classical solution was better'
            
            # Store result
            self.results_store[job_id] = final_result
            self.job_store[job_id]['status'] = 'completed'
            
            return final_result
            
        except Exception as e:
            self.job_store[job_id]['status'] = 'failed'
            self.job_store[job_id]['error'] = str(e)
            raise e
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get optimization job status"""
        return self.job_store.get(job_id)
    
    def get_result(self, result_id: str) -> Optional[Dict[str, Any]]:
        """Get optimization result by ID"""
        return self.results_store.get(result_id)
    
    def list_results(self, limit: int = 10) -> list:
        """List recent optimization results"""
        results = list(self.results_store.values())
        return sorted(results, key=lambda x: x.get('created_at', ''), reverse=True)[:limit]
