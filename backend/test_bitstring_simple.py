#!/usr/bin/env python3
"""
Quick test of bitstring decoding and repair functionality
"""

import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from quantum.qaoa_solver import QuantumOptimizer

def test_decode_and_repair():
    """Test the decoding and repair logic"""
    print("=" * 60)
    print("Testing Bitstring Decoding and Repair")
    print("=" * 60)
    
    # Setup test data
    warehouses = [
        {'id': 'W1', 'latitude': 40.7128, 'longitude': -74.0060, 'capacity': 100},
        {'id': 'W2', 'latitude': 41.8781, 'longitude': -87.6298, 'capacity': 80}
    ]
    
    customers = [
        {'id': 'C1', 'latitude': 42.3601, 'longitude': -71.0589, 'demand': 30},
        {'id': 'C2', 'latitude': 25.7617, 'longitude': -80.1918, 'demand': 40}
    ]
    
    distance_matrix = np.array([
        [100.0, 200.0],  # W1 to C1, C2
        [150.0, 180.0]   # W2 to C1, C2
    ])
    
    optimizer = QuantumOptimizer(backend='qasm_simulator', use_ibm=False)
    
    # Test 1: Valid bitstring
    print("\n✅ Test 1: Valid bitstring (1001 -> W1-C1, W2-C2)")
    bitstring = "1001"
    assignments, routes = optimizer._decode_and_repair_bitstring(
        bitstring, warehouses, customers, distance_matrix
    )
    print(f"   Assignments: {len(assignments)}")
    for a in assignments:
        print(f"   - {a['warehouse_id']} -> {a['customer_id']}: {a['distance_km']:.1f}km")
    assert len(assignments) == 2, "Should have 2 assignments"
    print("   ✓ PASS")
    
    # Test 2: No assignments (repair should assign to closest)
    print("\n✅ Test 2: No assignments (0000 -> repair to closest)")
    bitstring = "0000"
    assignments, routes = optimizer._decode_and_repair_bitstring(
        bitstring, warehouses, customers, distance_matrix
    )
    print(f"   Assignments: {len(assignments)}")
    for a in assignments:
        print(f"   - {a['warehouse_id']} -> {a['customer_id']}: {a['distance_km']:.1f}km")
    
    c1_assignment = next(a for a in assignments if a['customer_id'] == 'C1')
    c2_assignment = next(a for a in assignments if a['customer_id'] == 'C2')
    
    assert c1_assignment['warehouse_id'] == 'W1', "C1 should go to W1 (closest)"
    assert c2_assignment['warehouse_id'] == 'W2', "C2 should go to W2 (closest)"
    print("   ✓ PASS")
    
    # Test 3: Multiple assignments (repair should keep closest)
    print("\n✅ Test 3: Multiple assignments (1111 -> repair to closest)")
    bitstring = "1111"
    assignments, routes = optimizer._decode_and_repair_bitstring(
        bitstring, warehouses, customers, distance_matrix
    )
    print(f"   Assignments: {len(assignments)}")
    for a in assignments:
        print(f"   - {a['warehouse_id']} -> {a['customer_id']}: {a['distance_km']:.1f}km")
    
    c1_assignment = next(a for a in assignments if a['customer_id'] == 'C1')
    c2_assignment = next(a for a in assignments if a['customer_id'] == 'C2')
    
    assert c1_assignment['warehouse_id'] == 'W1', "C1 should keep W1 (closer)"
    assert c2_assignment['warehouse_id'] == 'W2', "C2 should keep W2 (closer)"
    print("   ✓ PASS")
    
    # Test 4: Compute metrics
    print("\n✅ Test 4: Compute metrics")
    metrics = optimizer._compute_metrics(assignments, routes, warehouses, customers)
    print(f"   Total cost: ${metrics['total_cost']:.2f}")
    print(f"   Total CO2: {metrics['total_co2']:.2f} kg")
    print(f"   Avg delivery time: {metrics['avg_delivery_time']:.2f} hours")
    print(f"   Routes used: {metrics['routes_used']}")
    
    assert metrics['total_cost'] > 0, "Cost should be positive"
    assert metrics['total_co2'] > 0, "CO2 should be positive"
    assert metrics['routes_used'] == 2, "Should have 2 routes"
    print("   ✓ PASS")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)

if __name__ == "__main__":
    test_decode_and_repair()
