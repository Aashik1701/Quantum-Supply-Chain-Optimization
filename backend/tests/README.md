# Backend Testing Guide

## Overview

This directory contains comprehensive tests for the Quantum Supply Chain Optimization backend API.

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_api_smoke.py        # Quick smoke tests for all endpoints
├── test_dashboard.py        # Dashboard functionality tests
├── test_optimization.py     # Optimization algorithm tests
└── test_data_validation.py  # Data validation tests (future)
```

## Test Categories

- **Smoke Tests** (`@pytest.mark.smoke`): Quick sanity checks
- **API Tests** (`@pytest.mark.api`): HTTP endpoint testing
- **Optimization Tests** (`@pytest.mark.optimization`): Algorithm testing
- **Data Tests** (`@pytest.mark.data`): Data handling and validation

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Or install minimal test dependencies:**
   ```bash
   pip install pytest pytest-flask
   ```

## Running Tests

### Using the test runner script:
```bash
python run_tests.py smoke          # Quick smoke tests
python run_tests.py api            # API endpoint tests
python run_tests.py optimization   # Optimization tests
python run_tests.py all            # All tests
python run_tests.py all --coverage # With coverage report
```

### Using pytest directly:
```bash
# All tests
pytest

# Smoke tests only
pytest -m smoke

# Specific test file
pytest tests/test_dashboard.py

# Specific test method
pytest tests/test_api_smoke.py::TestAPISmoke::test_health_endpoint

# With verbose output
pytest -v

# With coverage
pytest --cov=. --cov-report=term-missing
```

## Test Data

Tests use sample data fixtures defined in `conftest.py`:
- Sample warehouses (New York, Hamburg)
- Sample customers (London, Tokyo)
- Sample routes with different transport modes

## Expected Behavior

### Smoke Tests
- All API endpoints should return 200 OK
- Response format should follow standardized envelope
- Basic data structure validation

### Dashboard Tests
- Dashboard aggregates warehouse/customer/route counts
- Returns recent optimization results
- Responds within performance thresholds

### Optimization Tests
- Classical optimization should complete successfully
- Quantum optimization should fallback gracefully
- Hybrid optimization should combine approaches
- All methods should return valid cost/route data

## Continuous Integration

Add to CI pipeline:
```bash
# Quick validation
python run_tests.py smoke

# Full test suite
python run_tests.py all --coverage
```

## Troubleshooting

**Import errors:** Ensure you're running from the backend directory and have installed dependencies.

**Quantum dependency errors:** Use `requirements-dev.txt` which excludes heavy quantum libraries for faster testing.

**Database errors:** Tests use in-memory SQLite, no external database required.

## Adding New Tests

1. Create test files following `test_*.py` naming convention
2. Use appropriate pytest markers (`@pytest.mark.smoke`, etc.)
3. Import fixtures from `conftest.py`
4. Follow existing patterns for API testing with Flask test client

## Coverage Goals

- API endpoints: 90%+ coverage
- Core business logic: 80%+ coverage
- Edge cases and error handling: 70%+ coverage
