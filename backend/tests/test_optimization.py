"""
Happy path tests for optimization functionality
"""

import json


class TestOptimizationHappyPath:
    """Test successful optimization scenarios"""

    def test_classical_optimization_success(self, client, sample_optimization_data):
        """Test successful classical optimization"""
        payload = sample_optimization_data.copy()
        payload['method'] = 'classical'
        
        response = client.post(
            '/api/v1/optimize',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # The response structure is { data: { method, result } }
        response_data = data['data']
        assert response_data['method'] == 'classical'
        
        result = response_data['result']
        assert 'totalCost' in result
        assert 'totalCo2' in result
        assert 'routes' in result
        assert 'avgDeliveryTime' in result
        assert isinstance(result['routes'], list)

    def test_quantum_optimization_fallback(self, client, sample_optimization_data):
        """Test quantum optimization (should fallback to classical)"""
        payload = sample_optimization_data.copy()
        payload['method'] = 'quantum'
        
        response = client.post(
            '/api/v1/optimize',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        response_data = data['data']
        assert response_data['method'] == 'quantum'
        
        result = response_data['result']
        assert 'totalCost' in result
        assert 'routes' in result

    def test_hybrid_optimization_success(self, client, sample_optimization_data):
        """Test successful hybrid optimization"""
        payload = sample_optimization_data.copy()
        payload['method'] = 'hybrid'
        
        response = client.post(
            '/api/v1/optimize',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        response_data = data['data']
        assert response_data['method'] == 'hybrid'
        
        result = response_data['result']
        assert 'totalCost' in result
        assert 'routes' in result

    def test_optimization_with_parameters(self, client, sample_optimization_data):
        """Test optimization with custom parameters"""
        payload = sample_optimization_data.copy()
        payload['method'] = 'classical'
        payload['parameters'] = {
            'max_iterations': 100,
            'tolerance': 0.01
        }
        
        response = client.post(
            '/api/v1/optimize',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

    def test_optimization_result_structure(self, client, sample_optimization_data):
        """Test optimization result has expected structure"""
        response = client.post(
            '/api/v1/optimize',
            data=json.dumps(sample_optimization_data),
            content_type='application/json'
        )
        
        data = json.loads(response.data)['data']
        result = data['result']
        
        # Required fields in the result object
        required_fields = [
            'totalCost', 'totalCo2', 'avgDeliveryTime',
            'routesUsed', 'routes', 'assignments'
        ]
        
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        # Check method is at the top level
        assert 'method' in data

    def test_optimization_cost_calculation(self, client, sample_optimization_data):
        """Test optimization calculates costs correctly"""
        response = client.post(
            '/api/v1/optimize',
            data=json.dumps(sample_optimization_data),
            content_type='application/json'
        )
        
        data = json.loads(response.data)['data']
        result = data['result']
        
        assert result['totalCost'] >= 0
        assert result['totalCo2'] >= 0
        assert result['avgDeliveryTime'] >= 0
        # Should have routes if customers exist
        if sample_optimization_data['customers']:
            assert len(result['routes']) > 0
            assert len(result['assignments']) > 0

    def test_multiple_optimizations(self, client, sample_optimization_data):
        """Test running multiple optimizations"""
        methods = ['classical', 'quantum', 'hybrid']
        results = []
        for method in methods:
            payload = sample_optimization_data.copy()
            payload['method'] = method
            response = client.post(
                '/api/v1/optimize',
                data=json.dumps(payload),
                content_type='application/json'
            )
            assert response.status_code == 200
            data = json.loads(response.data)
            results.append(data['data'])
        # All should succeed
        assert len(results) == 3
        for result_data in results:
            result = result_data['result']
            assert 'totalCost' in result
            assert result_data['method'] in methods


class TestOptimizationValidation:
    """Test optimization input validation"""

    def test_optimization_requires_data(self, client):
        """Test optimization requires warehouse and customer data"""
        payload = {"method": "classical"}
        response = client.post(
            '/api/v1/optimize',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_optimization_with_empty_warehouses(self, client):
        """Test optimization with empty warehouses list"""
        payload = {
            "method": "classical",
            "warehouses": [],
            "customers": [{"id": "C1", "demand": 100}]
        }
        response = client.post(
            '/api/v1/optimize',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Should return validation error for empty warehouses
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data

    def test_optimization_invalid_json(self, client):
        """Test optimization with invalid JSON"""
        response = client.post(
            '/api/v1/optimize',
            data="invalid json",
            content_type='application/json'
        )
        
        assert response.status_code == 400
