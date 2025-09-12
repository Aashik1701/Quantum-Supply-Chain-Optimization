"""
Pytest configuration and fixtures for supply chain optimization tests
"""

import pytest
import os
import sys
from unittest.mock import Mock

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from services.data_service import DataService
from services.optimization_service import OptimizationService


@pytest.fixture
def app():
    """Create and configure a test Flask app"""
    app, socketio = create_app()
    app.config.update({
        "TESTING": True,
        "DEBUG": False,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False
    })
    
    # Create application context
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """Flask test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Flask test CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def sample_warehouses():
    """Sample warehouse data for testing"""
    return [
        {
            "id": "W1",
            "name": "New York Hub",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "capacity": 5000,
            "operating_cost": 1000,
            "country": "USA"
        },
        {
            "id": "W2",
            "name": "Hamburg Center",
            "latitude": 53.5511,
            "longitude": 9.9937,
            "capacity": 4200,
            "operating_cost": 800,
            "country": "Germany"
        }
    ]


@pytest.fixture
def sample_customers():
    """Sample customer data for testing"""
    return [
        {
            "id": "C1",
            "name": "London Store",
            "latitude": 51.5074,
            "longitude": -0.1278,
            "demand": 800,
            "priority": "high",
            "country": "UK"
        },
        {
            "id": "C2",
            "name": "Tokyo Retail",
            "latitude": 35.6762,
            "longitude": 139.6503,
            "demand": 1200,
            "priority": "medium",
            "country": "Japan"
        }
    ]


@pytest.fixture
def sample_routes():
    """Sample route data for testing"""
    return [
        {
            "id": "W1-C1-air",
            "warehouse_id": "W1",
            "customer_id": "C1",
            "transport_mode": "air",
            "cost_per_km": 2.5,
            "co2_per_km": 0.8,
            "speed_kmh": 800,
            "available": True
        },
        {
            "id": "W1-C2-sea",
            "warehouse_id": "W1",
            "customer_id": "C2",
            "transport_mode": "sea",
            "cost_per_km": 0.5,
            "co2_per_km": 0.2,
            "speed_kmh": 50,
            "available": True
        }
    ]


@pytest.fixture
def sample_optimization_data(sample_warehouses, sample_customers):
    """Complete optimization data for testing"""
    return {
        "warehouses": sample_warehouses,
        "customers": sample_customers,
        "method": "classical"
    }


@pytest.fixture
def data_service():
    """Data service instance for testing"""
    return DataService()


@pytest.fixture
def optimization_service():
    """Optimization service instance for testing"""
    return OptimizationService()


@pytest.fixture
def mock_quantum_available():
    """Mock quantum availability for testing"""
    with pytest.mock.patch('quantum.qaoa_solver.QISKIT_AVAILABLE', True):
        yield


@pytest.fixture
def mock_quantum_unavailable():
    """Mock quantum unavailability for testing"""
    with pytest.mock.patch('quantum.qaoa_solver.QISKIT_AVAILABLE', False):
        yield


@pytest.fixture
def sample_validation_data():
    """Sample data for validation testing"""
    return {
        "warehouses": [
            {
                "id": "W1",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "capacity": 5000
            }
        ],
        "customers": [
            {
                "id": "C1",
                "latitude": 51.5074,
                "longitude": -0.1278,
                "demand": 800
            }
        ],
        "routes": [
            {
                "warehouse_id": "W1",
                "customer_id": "C1",
                "transport_mode": "air",
                "cost_per_km": 2.5
            }
        ]
    }
