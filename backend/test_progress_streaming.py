#!/usr/bin/env python3
"""
Test WebSocket progress streaming during quantum optimization
"""

import sys
import os
import time
import numpy as np
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from quantum.qaoa_solver import QuantumOptimizer

def test_progress_streaming():
    """Test progress callback during optimization"""
    print("=" * 70)
    print("Testing Progress Streaming")
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
    
    # Track progress events
    progress_events = []
    
    def progress_callback(data):
        """Mock callback to capture progress"""
        progress_events.append(data)
        print(f"   Progress: iteration={data['iteration']}, energy={data['energy']:.4f}")
    
    print("\n🔬 Running QAOA with progress tracking...")
    optimizer = QuantumOptimizer(
        backend='qasm_simulator',
        use_ibm=False,
        progress_callback=progress_callback
    )
    
    result = optimizer.optimize(
        warehouses=warehouses,
        customers=customers,
        distance_matrix=distance_matrix,
        p_layers=1
    )
    
    print(f"\n✅ Optimization completed!")
    print(f"   Total progress events: {len(progress_events)}")
    print(f"   Final energy: {result.get('quantum_energy', 'N/A')}")
    print(f"   Backend: {result['backend_used']}")
    print(f"   Cost: ${result['total_cost']:.2f}")
    
    # Verify progress events
    assert len(progress_events) > 0, "Should have progress events"
    
    print(f"\n📊 Progress event details:")
    for i, event in enumerate(progress_events[:5]):  # Show first 5
        print(f"   Event {i+1}: iter={event['iteration']}, energy={event['energy']:.4f}")
    if len(progress_events) > 5:
        print(f"   ... and {len(progress_events) - 5} more events")
    
    # Check progress event structure
    for event in progress_events:
        assert 'iteration' in event, "Event should have iteration"
        assert 'energy' in event, "Event should have energy"
        assert 'timestamp' in event, "Event should have timestamp"
    
    print("\n" + "=" * 70)
    print("✅ Progress streaming test passed!")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    test_progress_streaming()
