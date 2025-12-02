#!/usr/bin/env python3
"""
Integration test for backend selection through optimization API
Tests the complete flow: API -> Service -> Quantum Optimizer
"""

import numpy as np
import sys
import os
from dotenv import load_dotenv

# Load .env from project root
load_dotenv()

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from quantum.qaoa_solver import QuantumOptimizer
from config.quantum_config import ibm_quantum

def test_backend_integration():
    """Test backend selection integration"""
    print("=" * 70)
    print("Backend Selection Integration Test")
    print("=" * 70)
    
    # Test data
    warehouses = [
        {'id': 'W1', 'latitude': 40.7128, 'longitude': -74.0060, 'capacity': 100},
        {'id': 'W2', 'latitude': 41.8781, 'longitude': -87.6298, 'capacity': 80}
    ]
    
    customers = [
        {'id': 'C1', 'latitude': 42.3601, 'longitude': -71.0589, 'demand': 30},
        {'id': 'C2', 'latitude': 25.7617, 'longitude': -80.1918, 'demand': 40}
    ]
    
    from utils.data_utils import haversine
    distance_matrix = np.array([
        [haversine(w['latitude'], w['longitude'], c['latitude'], c['longitude'])
         for c in customers]
        for w in warehouses
    ])
    
    # Test 1: Local simulator (default)
    print("\n✅ Test 1: Local simulator")
    optimizer = QuantumOptimizer(backend='qasm_simulator', use_ibm=False)
    result = optimizer.optimize(warehouses, customers, distance_matrix, p_layers=1)
    print(f"   Backend: {result['backend_used']}")
    print(f"   Method: {result.get('method', 'unknown')}")
    print(f"   Cost: ${result['total_cost']:.2f}")
    assert result['backend_used'] == 'qasm_simulator'
    assert result.get('method') == 'quantum'
    
    # Test 2: IBM backend with policy
    if ibm_quantum.initialize():
        print("\n✅ Test 2: IBM backend with 'device' policy")
        selected_backend = ibm_quantum.select_backend(policy='device')
        if selected_backend:
            print(f"   Selected: {selected_backend}")
            optimizer = QuantumOptimizer(backend=selected_backend, use_ibm=True)
            # Note: We won't actually run this to avoid queue time
            print(f"   ✓ Optimizer created with IBM backend")
        
        print("\n✅ Test 3: IBM backend with 'shortest_queue' policy")
        selected_backend = ibm_quantum.select_backend(policy='shortest_queue')
        if selected_backend:
            print(f"   Selected: {selected_backend}")
            backends_info = ibm_quantum.get_backends_info()
            device_info = next((d for d in backends_info['devices'] 
                              if d['name'] == selected_backend), None)
            if device_info:
                print(f"   Queue: {device_info.get('pending_jobs', 'N/A')} jobs")
            print(f"   ✓ Shortest queue backend selected")
    else:
        print("\n⚠️  Skipping IBM backend tests (not available)")
    
    # Test 4: Service integration (simulate what API does)
    print("\n✅ Test 4: Service-level integration")
    backend_policy = 'simulator'
    backend_name = None
    
    # This is what the service does
    selected_backend = None
    use_ibm = False
    
    if backend_name or backend_policy != 'simulator':
        if ibm_quantum.service or ibm_quantum.initialize():
            selected_backend = ibm_quantum.select_backend(backend_policy, backend_name)
            use_ibm = bool(selected_backend)
    
    if use_ibm and selected_backend:
        optimizer = QuantumOptimizer(backend=selected_backend, use_ibm=True)
        print(f"   Created IBM optimizer: {selected_backend}")
    else:
        optimizer = QuantumOptimizer(backend='qasm_simulator', use_ibm=False)
        print(f"   Created local optimizer: qasm_simulator")
    
    result = optimizer.optimize(warehouses, customers, distance_matrix, p_layers=1)
    print(f"   Result backend: {result['backend_used']}")
    print(f"   Cost: ${result['total_cost']:.2f}")
    assert result['backend_used'] in ['qasm_simulator', 'classical_fallback'] or result['backend_used'].startswith('ibm_')
    
    print("\n" + "=" * 70)
    print("✅ Backend selection integration tests passed!")
    print("=" * 70)

if __name__ == "__main__":
    test_backend_integration()
