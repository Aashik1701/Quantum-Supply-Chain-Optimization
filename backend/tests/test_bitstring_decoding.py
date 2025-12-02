"""
Unit tests for quantum bitstring decoding and feasibility repair
"""

import pytest
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from quantum.qaoa_solver import QuantumOptimizer


class TestBitstringDecoding:
    """Test bitstring decoding and repair functionality"""
    
    def setup_method(self):
        """Set up test data"""
        self.warehouses = [
            {'id': 'W1', 'latitude': 40.7128, 'longitude': -74.0060, 'capacity': 100},
            {'id': 'W2', 'latitude': 41.8781, 'longitude': -87.6298, 'capacity': 80}
        ]
        
        self.customers = [
            {'id': 'C1', 'latitude': 42.3601, 'longitude': -71.0589, 'demand': 30},
            {'id': 'C2', 'latitude': 25.7617, 'longitude': -80.1918, 'demand': 40}
        ]
        
        # Simple distance matrix (2 warehouses x 2 customers)
        self.distance_matrix = np.array([
            [100.0, 200.0],  # W1 to C1, C2
            [150.0, 180.0]   # W2 to C1, C2
        ])
        
        self.optimizer = QuantumOptimizer(backend='qasm_simulator', use_ibm=False)
    
    def test_decode_valid_bitstring(self):
        """Test decoding a valid bitstring with single assignments"""
        # Bitstring: "1001" -> W1-C1, W2-C2 (reading right to left)
        bitstring = "1001"
        
        assignments, routes = self.optimizer._decode_and_repair_bitstring(
            bitstring, self.warehouses, self.customers, self.distance_matrix
        )
        
        # Should have 2 assignments (one per customer)
        assert len(assignments) == 2
        assert len(routes) == 2
        
        # Verify each customer assigned exactly once
        customer_ids = [a['customer_id'] for a in assignments]
        assert set(customer_ids) == {'C1', 'C2'}
        assert len(customer_ids) == len(set(customer_ids))  # No duplicates
    
    def test_repair_no_assignment(self):
        """Test repair when customer has no assignment"""
        # Bitstring: "0000" -> no assignments
        bitstring = "0000"
        
        assignments, routes = self.optimizer._decode_and_repair_bitstring(
            bitstring, self.warehouses, self.customers, self.distance_matrix
        )
        
        # Should repair to assign each customer to closest warehouse
        assert len(assignments) == 2
        
        # C1 should go to W1 (100 < 150)
        c1_assignment = next(a for a in assignments if a['customer_id'] == 'C1')
        assert c1_assignment['warehouse_id'] == 'W1'
        assert c1_assignment['distance_km'] == 100.0
        
        # C2 should go to W2 (180 < 200)
        c2_assignment = next(a for a in assignments if a['customer_id'] == 'C2')
        assert c2_assignment['warehouse_id'] == 'W2'
        assert c2_assignment['distance_km'] == 180.0
    
    def test_repair_multiple_assignments(self):
        """Test repair when customer has multiple assignments"""
        # Bitstring: "1111" -> both warehouses assigned to both customers
        bitstring = "1111"
        
        assignments, routes = self.optimizer._decode_and_repair_bitstring(
            bitstring, self.warehouses, self.customers, self.distance_matrix
        )
        
        # Should repair to keep only closest warehouse per customer
        assert len(assignments) == 2
        
        # C1 should keep W1 (100 < 150)
        c1_assignment = next(a for a in assignments if a['customer_id'] == 'C1')
        assert c1_assignment['warehouse_id'] == 'W1'
        
        # C2 should keep W2 (180 < 200)
        c2_assignment = next(a for a in assignments if a['customer_id'] == 'C2')
        assert c2_assignment['warehouse_id'] == 'W2'
    
    def test_capacity_constraint_satisfied(self):
        """Test that capacity constraints are respected after repair"""
        # Small capacity warehouse
        warehouses_limited = [
            {'id': 'W1', 'capacity': 50},
            {'id': 'W2', 'capacity': 100}
        ]
        
        customers_high_demand = [
            {'id': 'C1', 'demand': 40},
            {'id': 'C2', 'demand': 35}
        ]
        
        # Bitstring assigns both to W1 (would exceed capacity 50)
        bitstring = "1010"
        
        assignments, routes = self.optimizer._decode_and_repair_bitstring(
            bitstring, warehouses_limited, customers_high_demand, self.distance_matrix
        )
        
        # Check total demand per warehouse
        w1_demand = sum(
            c['demand'] for i, c in enumerate(customers_high_demand)
            if any(a['customer_id'] == c['id'] and a['warehouse_id'] == 'W1' 
                   for a in assignments)
        )
        w2_demand = sum(
            c['demand'] for i, c in enumerate(customers_high_demand)
            if any(a['customer_id'] == c['id'] and a['warehouse_id'] == 'W2' 
                   for a in assignments)
        )
        
        # Capacity should be respected (may reassign one customer to W2)
        assert w1_demand <= 50 or w2_demand > 0  # Either W1 within capacity or some reassigned to W2
        assert len(assignments) == 2  # All customers still assigned
    
    def test_compute_metrics(self):
        """Test metric computation from assignments"""
        assignments = [
            {
                'warehouse_id': 'W1', 'customer_id': 'C1',
                'distance_km': 100.0, 'cost': 100.0,
                'co2': 40.0, 'delivery_time_hours': 1.25
            },
            {
                'warehouse_id': 'W2', 'customer_id': 'C2',
                'distance_km': 180.0, 'cost': 180.0,
                'co2': 72.0, 'delivery_time_hours': 2.25
            }
        ]
        
        routes = [
            {'id': 'W1-C1', 'warehouse_id': 'W1', 'customer_id': 'C1',
             'distance_km': 100.0, 'total_cost': 100.0, 'total_co2': 40.0,
             'delivery_time_hours': 1.25},
            {'id': 'W2-C2', 'warehouse_id': 'W2', 'customer_id': 'C2',
             'distance_km': 180.0, 'total_cost': 180.0, 'total_co2': 72.0,
             'delivery_time_hours': 2.25}
        ]
        
        metrics = self.optimizer._compute_metrics(
            assignments, routes, self.warehouses, self.customers
        )
        
        assert metrics['total_cost'] == 280.0
        assert metrics['total_co2'] == 112.0
        assert metrics['avg_delivery_time'] == 1.75
        assert metrics['routes_used'] == 2
        assert metrics['convergence'] is True
    
    def test_bitstring_length_handling(self):
        """Test handling of bitstrings with different lengths"""
        # Short bitstring (missing bits)
        short_bitstring = "10"
        
        assignments, routes = self.optimizer._decode_and_repair_bitstring(
            short_bitstring, self.warehouses, self.customers, self.distance_matrix
        )
        
        # Should still produce valid assignments via repair
        assert len(assignments) == 2
        assert all(a['customer_id'] in ['C1', 'C2'] for a in assignments)
        
        # Long bitstring (extra bits ignored)
        long_bitstring = "10011111"
        
        assignments, routes = self.optimizer._decode_and_repair_bitstring(
            long_bitstring, self.warehouses, self.customers, self.distance_matrix
        )
        
        # Should still produce valid assignments
        assert len(assignments) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
