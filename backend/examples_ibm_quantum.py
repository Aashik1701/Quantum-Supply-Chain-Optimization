"""
Quick example: Running quantum optimization on IBM Quantum Platform
"""

from quantum.qaoa_solver import QuantumOptimizer
import numpy as np

# Sample supply chain data
warehouses = [
    {'id': 'W1', 'latitude': 40.7128, 'longitude': -74.0060, 'capacity': 1000},
    {'id': 'W2', 'latitude': 34.0522, 'longitude': -118.2437, 'capacity': 1200}
]

customers = [
    {'id': 'C1', 'latitude': 41.8781, 'longitude': -87.6298, 'demand': 100},
    {'id': 'C2', 'latitude': 29.7604, 'longitude': -95.3698, 'demand': 150},
    {'id': 'C3', 'latitude': 33.4484, 'longitude': -112.0740, 'demand': 200}
]

# Distance matrix (in km)
distance_matrix = np.array([
    [1145, 1740, 2400],  # W1 to customers
    [2800, 2200, 600]    # W2 to customers
])


def example_1_local_simulator():
    """Example 1: Use local Qiskit simulator (fastest)"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Local Simulator")
    print("="*60)
    
    optimizer = QuantumOptimizer(
        backend='qasm_simulator',  # Local Aer simulator
        shots=1024
    )
    
    result = optimizer.optimize(
        warehouses=warehouses,
        customers=customers,
        distance_matrix=distance_matrix,
        p_layers=2  # QAOA depth
    )
    
    print(f"\n✓ Results:")
    print(f"  Total Cost: ${result['total_cost']:.2f}")
    print(f"  CO2 Emissions: {result['total_co2']:.2f} kg")
    print(f"  Routes Used: {result['routes_used']}")
    print(f"  Backend: {result['backend_used']}")
    print(f"  Time: {result['optimization_time']:.2f}s")
    
    return result


def example_2_ibm_cloud_simulator():
    """Example 2: Use IBM cloud simulator"""
    print("\n" + "="*60)
    print("EXAMPLE 2: IBM Cloud Simulator")
    print("="*60)
    
    optimizer = QuantumOptimizer(
        backend='ibmq_qasm_simulator',  # IBM cloud
        shots=1024,
        use_ibm=True  # Enable IBM Platform
    )
    
    result = optimizer.optimize(
        warehouses=warehouses,
        customers=customers,
        distance_matrix=distance_matrix,
        p_layers=2
    )
    
    print(f"\n✓ Results:")
    print(f"  Total Cost: ${result['total_cost']:.2f}")
    print(f"  Backend: {result['backend_used']}")
    print(f"  Time: {result['optimization_time']:.2f}s")
    
    return result


def example_3_real_quantum_hardware():
    """Example 3: Use real quantum computer"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Real Quantum Hardware")
    print("="*60)
    print("⚠️  This will submit to real quantum hardware queue")
    
    optimizer = QuantumOptimizer(
        backend='ibmq_manila',  # 5-qubit quantum computer
        shots=8192,  # More shots for noisy hardware
        use_ibm=True
    )
    
    # Smaller problem for real hardware
    small_warehouses = warehouses[:1]
    small_customers = customers[:2]
    small_distance_matrix = distance_matrix[:1, :2]
    
    result = optimizer.optimize(
        warehouses=small_warehouses,
        customers=small_customers,
        distance_matrix=small_distance_matrix,
        p_layers=1  # Shallow circuit for noisy hardware
    )
    
    print(f"\n✓ Results:")
    print(f"  Total Cost: ${result['total_cost']:.2f}")
    print(f"  Backend: {result['backend_used']}")
    print(f"  Time: {result['optimization_time']:.2f}s")
    
    return result


def example_4_compare_backends():
    """Example 4: Compare local vs IBM backends"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Backend Comparison")
    print("="*60)
    
    backends = [
        ('qasm_simulator', False),
        ('ibmq_qasm_simulator', True)
    ]
    
    results = {}
    
    for backend_name, use_ibm in backends:
        print(f"\nTesting {backend_name}...")
        
        try:
            optimizer = QuantumOptimizer(
                backend=backend_name,
                shots=1024,
                use_ibm=use_ibm
            )
            
            result = optimizer.optimize(
                warehouses=warehouses,
                customers=customers,
                distance_matrix=distance_matrix,
                p_layers=1
            )
            
            results[backend_name] = {
                'cost': result['total_cost'],
                'time': result['optimization_time']
            }
            
            print(f"  ✓ Cost: ${result['total_cost']:.2f}")
            print(f"  ✓ Time: {result['optimization_time']:.2f}s")
            
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            results[backend_name] = None
    
    print("\n" + "-"*60)
    print("Comparison:")
    for backend, data in results.items():
        if data:
            print(f"  {backend}: ${data['cost']:.2f} in {data['time']:.2f}s")
    
    return results


if __name__ == "__main__":
    import sys
    import os
    
    print("="*60)
    print("IBM Quantum Platform - Example Usage")
    print("="*60)
    
    # Check token
    if not os.environ.get('IBM_QUANTUM_TOKEN'):
        print("\n⚠️  IBM_QUANTUM_TOKEN not set!")
        print("Only local simulator will work.")
        print("\nTo enable IBM backends:")
        print("1. Get token: https://quantum-computing.ibm.com/")
        print("2. Add to .env: IBM_QUANTUM_TOKEN=your_token")
        print("")
    
    while True:
        print("\nSelect example to run:")
        print("  1. Local Simulator (fast, no token needed)")
        print("  2. IBM Cloud Simulator (requires token)")
        print("  3. Real Quantum Hardware (requires token, queue wait)")
        print("  4. Compare Backends")
        print("  0. Exit")
        
        choice = input("\nChoice: ").strip()
        
        if choice == '1':
            example_1_local_simulator()
        elif choice == '2':
            example_2_ibm_cloud_simulator()
        elif choice == '3':
            confirm = input("Run on real hardware? (yes/no): ").lower()
            if confirm == 'yes':
                example_3_real_quantum_hardware()
        elif choice == '4':
            example_4_compare_backends()
        elif choice == '0':
            break
        else:
            print("Invalid choice")
    
    print("\n✓ Done!")
