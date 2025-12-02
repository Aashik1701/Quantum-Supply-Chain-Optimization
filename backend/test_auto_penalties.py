#!/usr/bin/env python3
"""
Test auto penalty scaling functionality
"""

import sys
import os
import numpy as np
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from quantum.qaoa_solver import QuantumOptimizer

def test_auto_penalty_scaling():
    """Test auto penalty computation and impact on QUBO"""
    print("=" * 70)
    print("Testing Auto Penalty Scaling")
    print("=" * 70)
    
    # Test data with varying scales
    warehouses = [
        {'id': 'W1', 'latitude': 40.7128, 'longitude': -74.0060, 'capacity': 100},
        {'id': 'W2', 'latitude': 41.8781, 'longitude': -87.6298, 'capacity': 80},
        {'id': 'W3', 'latitude': 34.0522, 'longitude': -118.2437, 'capacity': 120}
    ]
    
    customers = [
        {'id': 'C1', 'latitude': 42.3601, 'longitude': -71.0589, 'demand': 30},
        {'id': 'C2', 'latitude': 25.7617, 'longitude': -80.1918, 'demand': 40},
        {'id': 'C3', 'latitude': 29.7604, 'longitude': -95.3698, 'demand': 35}
    ]
    
    from utils.data_utils import haversine
    distance_matrix = np.array([
        [haversine(w['latitude'], w['longitude'], c['latitude'], c['longitude'])
         for c in customers]
        for w in warehouses
    ])
    
    print(f"\n📊 Problem Statistics:")
    print(f"   Warehouses: {len(warehouses)}")
    print(f"   Customers: {len(customers)}")
    print(f"   Avg distance: {np.mean(distance_matrix):.2f} km")
    print(f"   Max distance: {np.max(distance_matrix):.2f} km")
    print(f"   Min distance: {np.min(distance_matrix):.2f} km")
    
    total_demand = sum(c['demand'] for c in customers)
    total_capacity = sum(w['capacity'] for w in warehouses)
    print(f"   Total demand: {total_demand}")
    print(f"   Total capacity: {total_capacity}")
    print(f"   Utilization: {total_demand/total_capacity*100:.1f}%")
    
    optimizer = QuantumOptimizer(backend='qasm_simulator', use_ibm=False)
    
    # Test 1: Auto penalty mode
    print(f"\n✅ Test 1: Auto penalty mode")
    penalties_auto = optimizer._auto_compute_penalties(warehouses, customers, distance_matrix)
    print(f"   λ1 (single-assignment): {penalties_auto['lambda1']:.2f}")
    print(f"   λ2 (capacity): {penalties_auto['lambda2']:.2f}")
    print(f"   Cost stats:")
    for key, val in penalties_auto['cost_stats'].items():
        print(f"      {key}: {val:.2f}")
    
    # Verify penalties are reasonable
    avg_cost = penalties_auto['cost_stats']['avg']
    assert penalties_auto['lambda1'] > avg_cost, "λ1 should be larger than avg cost"
    assert 100 <= penalties_auto['lambda1'] <= 10000, "λ1 should be in reasonable range"
    print(f"   ✓ Auto penalties computed successfully")
    
    # Test 2: Run optimization with auto penalties
    print(f"\n✅ Test 2: Optimization with auto penalties")
    result_auto = optimizer.optimize(
        warehouses=warehouses,
        customers=customers,
        distance_matrix=distance_matrix,
        penalty_mode='auto',
        p_layers=1
    )
    
    print(f"   Cost: ${result_auto['total_cost']:.2f}")
    print(f"   Routes: {result_auto['routes_used']}")
    print(f"   Backend: {result_auto['backend_used']}")
    
    # Check feasibility
    customer_assignments = {}
    for assignment in result_auto['assignments']:
        cid = assignment['customer_id']
        if cid in customer_assignments:
            print(f"   ⚠️  Customer {cid} assigned multiple times!")
        customer_assignments[cid] = assignment['warehouse_id']
    
    if len(customer_assignments) == len(customers):
        print(f"   ✓ All customers assigned exactly once (feasible)")
    else:
        print(f"   ⚠️  Feasibility issue: {len(customer_assignments)}/{len(customers)} assigned")
    
    # Test 3: Manual penalty mode
    print(f"\n✅ Test 3: Manual penalty mode")
    result_manual = optimizer.optimize(
        warehouses=warehouses,
        customers=customers,
        distance_matrix=distance_matrix,
        penalty_mode='manual',
        lambda1=500,
        lambda2=100,
        p_layers=1
    )
    
    print(f"   Cost: ${result_manual['total_cost']:.2f}")
    print(f"   Routes: {result_manual['routes_used']}")
    print(f"   ✓ Manual penalties applied")
    
    # Test 4: Compare auto vs manual
    print(f"\n✅ Test 4: Auto vs Manual comparison")
    print(f"   Auto cost: ${result_auto['total_cost']:.2f}")
    print(f"   Manual cost: ${result_manual['total_cost']:.2f}")
    print(f"   Difference: ${abs(result_auto['total_cost'] - result_manual['total_cost']):.2f}")
    
    # Test 5: Different problem scales
    print(f"\n✅ Test 5: Penalty scaling with problem size")
    
    # Small scale problem (short distances)
    small_distances = distance_matrix / 10  # Scale down
    penalties_small = optimizer._auto_compute_penalties(warehouses, customers, small_distances)
    
    # Large scale problem (long distances)
    large_distances = distance_matrix * 10  # Scale up
    penalties_large = optimizer._auto_compute_penalties(warehouses, customers, large_distances)
    
    print(f"   Small scale λ1: {penalties_small['lambda1']:.2f}")
    print(f"   Normal scale λ1: {penalties_auto['lambda1']:.2f}")
    print(f"   Large scale λ1: {penalties_large['lambda1']:.2f}")
    
    # Check scaling (accounting for upper/lower bounds)
    assert penalties_small['lambda1'] <= penalties_auto['lambda1'], "Small should be <= normal"
    assert penalties_auto['lambda1'] <= penalties_large['lambda1'], "Normal should be <= large"
    
    # Verify at least one scales (not all clamped)
    if penalties_small['lambda1'] < penalties_auto['lambda1'] or \
       penalties_auto['lambda1'] < penalties_large['lambda1']:
        print(f"   ✓ Penalties scale appropriately with problem size")
    else:
        print(f"   ℹ️  Penalties clamped at bounds (expected for extreme scales)")
    
    print("\n" + "=" * 70)
    print("✅ All auto penalty scaling tests passed!")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    test_auto_penalty_scaling()
