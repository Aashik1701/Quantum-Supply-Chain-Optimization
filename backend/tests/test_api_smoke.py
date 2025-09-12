"""
Smoke tests for API endpoints - quick sanity checks
"""

import pytest
import json


@pytest.mark.smoke
@pytest.mark.api
class TestAPISmoke:
    """Basic smoke tests to ensure API endpoints are responding"""

    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] == 'healthy'

    def test_api_health_endpoint(self, client):
        """Test API health check endpoint"""
        response = client.get('/api/v1/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data

    def test_dashboard_endpoint(self, client):
        """Test dashboard endpoint returns data"""
        response = client.get('/api/v1/dashboard')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'summary' in data['data']
        assert 'warehouses' in data['data']['summary']
        assert 'customers' in data['data']['summary']
        assert 'routes' in data['data']['summary']

    def test_warehouses_endpoint(self, client):
        """Test warehouses data endpoint"""
        response = client.get('/api/v1/data/warehouses')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert isinstance(data['data'], list)

    def test_customers_endpoint(self, client):
        """Test customers data endpoint"""
        response = client.get('/api/v1/data/customers')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert isinstance(data['data'], list)

    def test_routes_endpoint(self, client):
        """Test routes data endpoint"""
        response = client.get('/api/v1/data/routes')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert isinstance(data['data'], list)

    def test_invalid_endpoint_404(self, client):
        """Test that invalid endpoints return 404"""
        response = client.get('/api/v1/nonexistent')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'NOT_FOUND'

    def test_cors_headers(self, client):
        """Test CORS headers are present"""
        response = client.options('/api/v1/health')
        # Should not fail - basic CORS check
        assert response.status_code in [200, 204]


@pytest.mark.smoke
@pytest.mark.optimization
class TestOptimizationSmoke:
    """Smoke tests for optimization endpoints"""

    def test_optimize_endpoint_missing_data(self, client):
        """Test optimize endpoint with missing data"""
        response = client.post('/api/v1/optimize')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'VALIDATION_ERROR'

    def test_optimize_endpoint_invalid_method(self, client):
        """Test optimize endpoint with invalid method"""
        payload = {
            "method": "invalid_method",
            "warehouses": [],
            "customers": []
        }
        response = client.post(
            '/api/v1/optimize',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'VALIDATION_ERROR'


@pytest.mark.smoke
@pytest.mark.data
class TestDataValidationSmoke:
    """Smoke tests for data validation"""

    def test_validation_endpoint_empty_data(self, client):
        """Test validation with empty data"""
        payload = {}
        response = client.post(
            '/api/v1/data/validate',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_validation_endpoint_missing_data(self, client):
        """Test validation endpoint with no data"""
        response = client.post('/api/v1/data/validate')
        assert response.status_code == 400


@pytest.mark.smoke
@pytest.mark.upload
class TestUploadSmoke:
    """Smoke tests for file upload functionality"""

    def test_upload_no_file(self, client):
        """Test upload endpoint with no file"""
        response = client.post('/api/v1/data/upload')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'VALIDATION_ERROR'

    def test_upload_invalid_file_type(self, client):
        """Test upload with invalid file type"""
        from io import StringIO
        
        data = {
            'file': (StringIO('test'), 'test.txt'),
            'type': 'warehouses'
        }
        response = client.post(
            '/api/v1/data/upload',
            data=data,
            content_type='multipart/form-data'
        )
        assert response.status_code == 400

    def test_upload_invalid_data_type(self, client):
        """Test upload with invalid data type"""
        from io import StringIO
        
        csv_content = "id,name,country\nW1,Test Warehouse,USA"
        data = {
            'file': (StringIO(csv_content), 'test.csv'),
            'type': 'invalid_type'
        }
        response = client.post(
            '/api/v1/data/upload',
            data=data,
            content_type='multipart/form-data'
        )
        assert response.status_code == 400

    def test_upload_empty_file(self, client):
        """Test upload with empty file"""
        from io import StringIO
        
        data = {
            'file': (StringIO(''), 'empty.csv'),
            'type': 'warehouses'
        }
        response = client.post(
            '/api/v1/data/upload',
            data=data,
            content_type='multipart/form-data'
        )
        assert response.status_code == 400
