"""
Test QUBO size reduction capabilities
"""
import numpy as np
from quantum.hybrid_integration import (
    cluster_customers,
    eliminate_dominated_pairs,
    expand_solution,
    generate_warm_start_params,
    reduce_problem,
)

print("=" * 70)
print("Testing QUBO Size Reduction")
print("=" * 70)

# Test 1: Customer Clustering
print("\n✅ Test 1: Customer clustering")
customers = [
    {'id': f'C{i}', 'latitude': 40.0 + i * 0.1, 'longitude': -74.0 + i * 0.1, 'demand': 100}
    for i in range(100)
]

cluster_reps, cluster_mapping = cluster_customers(customers, max_cluster_size=20)
print(f"   Clustered {len(customers)} customers into {len(cluster_reps)} clusters")
print(f"   Cluster sizes: {[len(v) for v in cluster_mapping.values()]}")
assert len(cluster_reps) > 0 and len(cluster_reps) < len(customers)
print("   ✓ Clustering reduced problem size")

# Test 2: Variable Elimination
print("\n✅ Test 2: Dominated pair elimination")
warehouses = [
    {'id': 'W1', 'latitude': 40.0, 'longitude': -74.0, 'capacity': 1000},
    {'id': 'W2', 'latitude': 41.0, 'longitude': -75.0, 'capacity': 1000},
    {'id': 'W3', 'latitude': 42.0, 'longitude': -76.0, 'capacity': 1000},
]
test_customers = [
    {'id': 'C1', 'latitude': 40.1, 'longitude': -74.1, 'demand': 50},
    {'id': 'C2', 'latitude': 41.9, 'longitude': -75.9, 'demand': 50},
]

# Simple distance matrix
distance_matrix = np.array([
    [10, 200],   # W1 close to C1, far from C2
    [150, 150],  # W2 moderate to both
    [200, 10],   # W3 far from C1, close to C2
])

valid_mask, eliminated = eliminate_dominated_pairs(
    warehouses, test_customers, distance_matrix, cost_threshold=2.0
)
print(f"   Eliminated {len(eliminated)} pairs out of {distance_matrix.size}")
print(f"   Valid pairs: {valid_mask.sum()} / {distance_matrix.size}")
assert len(eliminated) > 0
print("   ✓ Eliminated dominated pairs")

# Test 3: Solution Expansion
print("\n✅ Test 3: Solution expansion")
reduced_solution = {
    'CLUSTER_0': 'W1',
    'CLUSTER_1': 'W2',
}
full_solution = expand_solution(reduced_solution, cluster_mapping, warehouses, customers)
print(f"   Expanded {len(reduced_solution)} cluster assignments to {len(full_solution)} customers")
assert len(full_solution) == len(customers)
print("   ✓ All customers assigned after expansion")

# Test 4: Warm-start Parameters
print("\n✅ Test 4: Warm-start parameter generation")
classical_solution = {c['id']: warehouses[i % len(warehouses)]['id'] 
                     for i, c in enumerate(customers[:10])}
warm_params = generate_warm_start_params(
    classical_solution, warehouses, customers[:10], num_params=2
)
print(f"   Generated warm-start params: {warm_params}")
assert len(warm_params) == 4  # 2 gammas + 2 betas
assert np.all(warm_params >= 0) and np.all(warm_params <= np.pi)
print("   ✓ Valid warm-start parameters generated")

# Test 5: Full Reduction Pipeline
print("\n✅ Test 5: Full reduction pipeline")
large_customers = [
    {'id': f'C{i}', 'latitude': 40.0 + i * 0.01, 'longitude': -74.0 + i * 0.01, 'demand': 100}
    for i in range(80)
]
large_distance = np.random.rand(len(warehouses), len(large_customers)) * 1000

reduction_info = reduce_problem(
    warehouses, large_customers, large_distance,
    max_customers=50,
    enable_clustering=True,
    enable_elimination=True,
)

print(f"   Original size: {reduction_info['original_sizes']}")
print(f"   Reduced size: {reduction_info['reduced_sizes']}")
print(f"   Clusters: {len(reduction_info['cluster_mapping'])}")
print(f"   Valid pairs: {reduction_info['valid_pairs_mask'].sum() if reduction_info['valid_pairs_mask'] is not None else 'N/A'}")

assert reduction_info['reduced_sizes'][1] < reduction_info['original_sizes'][1]
print("   ✓ Problem size successfully reduced")

print("\n" + "=" * 70)
print("✅ All QUBO reduction tests passed!")
print("=" * 70)
