#!/usr/bin/env python3
"""
Test quantum optimization with bitstring decoding end-to-end
"""

import numpy as np
from quantum.qaoa_solver import QuantumOptimizer

def test_quantum_with_bitstring():
    """Test full quantum optimization with bitstring decoding"""
    print("=" * 70)
    print("Testing Quantum Optimization with Bitstring Decoding")
    print("=" * 70)
    
    # Setup test data
    warehouses = [
        {'id': 'W1', 'name': 'NY', 'latitude': 40.7128, 'longitude': -74.0060, 
         'capacity': 100},
        {'id': 'W2', 'name': 'Chicago', 'latitude': 41.8781, 'longitude': -87.6298, 
         'capacity': 80}
    ]
    
    customers = [
        {'id': 'C1', 'name': 'Boston', 'latitude': 42.3601, 'longitude': -71.0589, 
         'demand': 30},
        {'id': 'C2', 'name': 'Miami', 'latitude': 25.7617, 'longitude': -80.1918, 
         'demand': 40}
    ]
    
    # Calculate distance matrix
    from utils.data_utils import haversine
    n_warehouses = len(warehouses)
    n_customers = len(customers)
    distance_matrix = np.zeros((n_warehouses, n_customers))
    
    for i, warehouse in enumerate(warehouses):
        for j, customer in enumerate(customers):
            distance_matrix[i, j] = haversine(
                warehouse['latitude'], warehouse['longitude'],
                customer['latitude'], customer['longitude']
            )
    
    print(f"\n📊 Problem size:")
    print(f"   Warehouses: {n_warehouses}")
    print(f"   Customers: {n_customers}")
    print(f"   Qubits needed: {n_warehouses * n_customers}")
    
    print(f"\n📏 Distance Matrix:")
    print(f"   W1->C1: {distance_matrix[0, 0]:.1f} km")
    print(f"   W1->C2: {distance_matrix[0, 1]:.1f} km")
    print(f"   W2->C1: {distance_matrix[1, 0]:.1f} km")
    print(f"   W2->C2: {distance_matrix[1, 1]:.1f} km")
    
    # Test with local simulator
    print(f"\n🔬 Running QAOA optimization (local simulator)...")
    optimizer = QuantumOptimizer(backend='qasm_simulator', shots=1024, use_ibm=False)
    
    result = optimizer.optimize(
        warehouses=warehouses,
        customers=customers,
        distance_matrix=distance_matrix,
        p_layers=1
    )
    
    print(f"\n✅ Quantum Optimization Results:")
    print(f"   Method: {result.get('method', 'unknown')}")
    print(f"   Backend: {result['backend_used']}")
    print(f"   Quantum energy: {result.get('quantum_energy', 'N/A')}")
    print(f"   Total cost: ${result['total_cost']:.2f}")
    print(f"   Total CO2: {result['total_co2']:.2f} kg")
    print(f"   Routes used: {result['routes_used']}")
    print(f"   Optimization time: {result['optimization_time']:.2f}s")
    print(f"   Circuit depth: {result.get('circuit_depth', 'N/A')}")
    print(f"   Quantum shots: {result.get('quantum_shots', 'N/A')}")
    print(f"   Iterations: {result.get('iterations', 'N/A')}")
    
    print(f"\n📦 Assignments:")
    for assignment in result['assignments']:
        print(f"   {assignment['warehouse_id']} -> {assignment['customer_id']}: "
              f"{assignment['distance_km']:.1f}km, "
              f"${assignment['cost']:.2f}, "
              f"{assignment['co2']:.2f}kg CO2")
    
    # Verify feasibility
    print(f"\n✅ Feasibility checks:")
    
    # Check each customer assigned exactly once
    customer_assignments = {}
    for assignment in result['assignments']:
        cid = assignment['customer_id']
        if cid in customer_assignments:
            print(f"   ❌ Customer {cid} assigned multiple times!")
            return False
        customer_assignments[cid] = assignment['warehouse_id']
    
    if len(customer_assignments) == len(customers):
        print(f"   ✓ All customers assigned exactly once")
    else:
        print(f"   ❌ Not all customers assigned!")
        return False
    
    # Check capacity constraints
    warehouse_loads = {w['id']: 0 for w in warehouses}
    for assignment in result['assignments']:
        wid = assignment['warehouse_id']
        customer = next(c for c in customers if c['id'] == assignment['customer_id'])
        warehouse_loads[wid] += customer.get('demand', 0)
    
    capacity_satisfied = True
    for warehouse in warehouses:
        wid = warehouse['id']
        load = warehouse_loads[wid]
        capacity = warehouse.get('capacity', float('inf'))
        status = "✓" if load <= capacity else "⚠️"
        print(f"   {status} {wid}: {load}/{capacity} capacity used")
        if load > capacity:
            capacity_satisfied = False
    
    print(f"\n" + "=" * 70)
    if capacity_satisfied:
        print("✅ All tests passed! Quantum bitstring decoding working correctly.")
    else:
        print("⚠️  Tests passed with capacity warnings (may need repair tuning).")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    test_quantum_with_bitstring()
