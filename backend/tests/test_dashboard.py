"""
Tests for dashboard functionality
"""

import json


class TestDashboard:
    """Test dashboard endpoint and data aggregation"""

    def test_dashboard_structure(self, client):
        """Test dashboard returns expected data structure"""
        response = client.get('/api/v1/dashboard')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        
        dashboard_data = data['data']
        assert 'summary' in dashboard_data
        assert 'recentResults' in dashboard_data
        
        summary = dashboard_data['summary']
        assert 'warehouses' in summary
        assert 'customers' in summary
        assert 'routes' in summary
        assert 'recentOptimizations' in summary

    def test_dashboard_summary_counts(self, client):
        """Test dashboard summary contains valid counts"""
        response = client.get('/api/v1/dashboard')
        data = json.loads(response.data)['data']
        
        summary = data['summary']
        assert isinstance(summary['warehouses'], int)
        assert isinstance(summary['customers'], int)
        assert isinstance(summary['routes'], int)
        assert isinstance(summary['recentOptimizations'], int)
        
        # Should have sample data
        assert summary['warehouses'] > 0
        assert summary['customers'] > 0
        assert summary['routes'] > 0

    def test_dashboard_recent_results(self, client):
        """Test dashboard recent results structure"""
        response = client.get('/api/v1/dashboard')
        data = json.loads(response.data)['data']
        
        recent_results = data['recentResults']
        assert isinstance(recent_results, list)
        # Initially empty since no optimizations run
        assert len(recent_results) == 0

    def test_dashboard_after_optimization(self, client, sample_optimization_data):
        """Test dashboard updates after running optimization"""
        # First run an optimization
        response = client.post(
            '/api/v1/optimize',
            data=json.dumps(sample_optimization_data),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # Then check dashboard
        response = client.get('/api/v1/dashboard')
        data = json.loads(response.data)['data']
        
        summary = data['summary']
        assert summary['recentOptimizations'] == 1
        
        recent_results = data['recentResults']
        assert len(recent_results) == 1
        
        result = recent_results[0]
        assert 'totalCost' in result
        assert 'totalCo2' in result
        assert 'method' in result

    def test_dashboard_performance(self, client):
        """Test dashboard endpoint responds quickly"""
        import time
        
        start_time = time.time()
        response = client.get('/api/v1/dashboard')
        end_time = time.time()
        
        assert response.status_code == 200
        # Should respond within 1 second
        assert (end_time - start_time) < 1.0
