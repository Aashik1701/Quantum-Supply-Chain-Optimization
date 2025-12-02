#!/usr/bin/env python3
"""
Test script for IBM Quantum Platform integration
Run this to verify your IBM Quantum setup
"""

import os
import sys
from pathlib import Path

# Load environment variables from project .env
try:
    from dotenv import load_dotenv
    root_env = Path(__file__).resolve().parents[1] / ".env"
    if root_env.exists():
        load_dotenv(dotenv_path=root_env)
except Exception:
    pass

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from config.quantum_config import test_ibm_connection, ibm_quantum
from quantum.qaoa_solver import QuantumOptimizer


def test_local_simulator():
    """Test local Qiskit simulator"""
    print("\n" + "="*60)
    print("TEST 1: Local Qiskit Simulator")
    print("="*60)
    
    try:
        optimizer = QuantumOptimizer(backend='qasm_simulator', shots=1024)
        
        # Simple test data
        warehouses = [
            {'id': 'W1', 'latitude': 40.7128, 'longitude': -74.0060},
            {'id': 'W2', 'latitude': 34.0522, 'longitude': -118.2437}
        ]
        
        customers = [
            {'id': 'C1', 'latitude': 41.8781, 'longitude': -87.6298, 'demand': 100},
            {'id': 'C2', 'latitude': 29.7604, 'longitude': -95.3698, 'demand': 150}
        ]
        
        import numpy as np
        distance_matrix = np.array([[100, 200], [300, 150]])
        
        print("\n🔬 Running quantum optimization (local simulator)...")
        result = optimizer.optimize(warehouses, customers, distance_matrix, p_layers=1)
        
        print(f"\n✓ Optimization completed!")
        print(f"  Total cost: ${result['total_cost']:.2f}")
        print(f"  Routes used: {result.get('routes_used', len(result.get('routes', [])))}")
        print(f"  Backend: {result['backend_used']}")
        print(f"  Optimization time: {result['optimization_time']:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Local simulator test failed: {e}")
        return False


def test_ibm_connectivity_only():
    """Test IBM cloud connectivity and backend availability (no circuit run)."""
    print("\n" + "="*60)
    print("TEST 2: IBM Cloud Connectivity")
    print("="*60)
    
    token_present = bool(os.environ.get('IBM_QUANTUM_TOKEN'))
    if not token_present:
        print("\n⚠️  IBM_QUANTUM_TOKEN not set in environment")
        print("Skipping IBM connectivity test")
        print("\nTo enable:")
        print("1. Get token from: https://quantum-computing.ibm.com/")
        print("2. Add to .env: IBM_QUANTUM_TOKEN=your_token_here")
        return False
    
    try:
        # Ensure service is initialized (test_ibm_connection already does this)
        if not ibm_quantum.service and not ibm_quantum.initialize():
            print("❌ Could not initialize IBM Quantum service")
            return False

        service = ibm_quantum.service
        backends = service.backends()
        if not backends:
            print("❌ No backends available for this account")
            return False

        # Prefer a simulator if present, else pick the first hardware
        preferred = None
        for b in backends:
            try:
                if getattr(b.configuration(), 'simulator', False):
                    preferred = b
                    break
            except Exception:
                continue
        if preferred is None:
            preferred = backends[0]

        print(f"\n✓ IBM Quantum connection verified; sample backend: {preferred.name}")
        return True
    except Exception as e:
        print(f"\n❌ IBM connectivity test failed: {e}")
        return False


def main():
    """Run tests"""
    print("="*60)
    print("IBM Quantum Platform Integration Test Suite")
    print("="*60)
    
    results = {}
    
    # Test 0: IBM Connection + list backends
    print("\n🔗 Testing IBM Quantum Platform connection...")
    results['ibm_connection'] = test_ibm_connection()
    
    # Test 1: Local Simulator (always run)
    results['local_simulator'] = test_local_simulator()
    
    # Test 2: IBM Connectivity (skip if no token)
    results['ibm_connectivity'] = test_ibm_connectivity_only()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        if passed is None:
            status = "⊝ SKIPPED"
        elif passed:
            status = "✓ PASSED"
        else:
            status = "✗ FAILED"
        print(f"{status:12} {test_name}")
    
    print("="*60)
    
    # Exit code
    if all(r for r in results.values() if r is not None):
        print("\n✓ All applicable tests passed!")
        return 0
    else:
        print("\nSome tests failed or were skipped.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
