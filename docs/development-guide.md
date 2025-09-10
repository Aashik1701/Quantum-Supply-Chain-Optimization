# Development Guide

## Overview

This guide provides comprehensive instructions for developers working on the Hybrid Quantum-Classical Supply Chain Optimization project. It covers development environment setup, coding standards, testing procedures, and contribution workflows.

## Development Environment Setup

### Prerequisites

Before starting development, ensure you have the following installed:

- **Python 3.8+** with pip and virtualenv
- **Node.js 16+** with npm or yarn
- **Git** for version control
- **Docker** and Docker Compose (recommended)
- **Visual Studio Code** (recommended IDE)
- **PostgreSQL 13+** (if not using Docker)
- **Redis 6+** (if not using Docker)

### Initial Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/your-username/hybrid-quantum-supply-chain.git
cd hybrid-quantum-supply-chain
```

#### 2. Environment Configuration

Create environment files from templates:

```bash
# Root environment file
cp .env.example .env

# Backend environment
cp backend/.env.example backend/.env

# Frontend environment  
cp frontend/.env.example frontend/.env.local
```

Edit the `.env` files with your configuration:

```bash
# .env (Root)
COMPOSE_PROJECT_NAME=supply_chain_optimization
POSTGRES_DB=supply_chain
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
REDIS_PASSWORD=your_redis_password

# backend/.env
FLASK_ENV=development
FLASK_APP=app.py
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://postgres:password@localhost:5432/supply_chain
REDIS_URL=redis://localhost:6379
QISKIT_DEVICE=simulator
IBM_QUANTUM_TOKEN=your-ibm-quantum-token-optional

# frontend/.env.local
REACT_APP_API_URL=http://localhost:5000
REACT_APP_MAPBOX_TOKEN=your-mapbox-access-token
REACT_APP_WS_URL=ws://localhost:5000/socket.io
```

### Backend Development Setup

#### Using Virtual Environment (Recommended for Development)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Set up database
python -c "
from app import create_app
from models import db
app = create_app()
with app.app_context():
    db.create_all()
"

# Run the development server
python app.py
```

#### Using Docker (Recommended for Quick Setup)

```bash
# Start backend services
docker-compose up -d postgres redis

# Run backend in development mode
cd backend
docker build -t supply-chain-backend .
docker run -p 5000:5000 --env-file .env supply-chain-backend
```

### Frontend Development Setup

#### Using npm

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Or using yarn
yarn install
yarn start
```

#### Using Docker

```bash
cd frontend
docker build -t supply-chain-frontend .
docker run -p 3000:3000 supply-chain-frontend
```

### Full Stack Development with Docker Compose

```bash
# Start all services
docker-compose -f docker-compose.dev.yml up --build

# Start specific services
docker-compose -f docker-compose.dev.yml up postgres redis backend

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop all services
docker-compose down
```

## Development Workflow

### Git Workflow

We use **GitFlow** with the following branches:

- `main`: Production-ready code
- `develop`: Integration branch for development
- `feature/*`: Feature development branches
- `hotfix/*`: Critical bug fixes
- `release/*`: Release preparation branches

#### Creating a Feature Branch

```bash
# Update develop branch
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/quantum-algorithm-improvements

# Make your changes and commit
git add .
git commit -m "feat: improve QAOA convergence algorithm"

# Push feature branch
git push origin feature/quantum-algorithm-improvements

# Create pull request on GitHub
```

#### Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/modifications
- `chore`: Build process or auxiliary tool changes

**Examples:**
```bash
git commit -m "feat(quantum): add noise model support to QAOA"
git commit -m "fix(api): resolve memory leak in optimization service"
git commit -m "docs(readme): update installation instructions"
git commit -m "test(optimization): add unit tests for hybrid coordinator"
```

### Code Style and Formatting

#### Python (Backend)

We use **Black** for code formatting and **flake8** for linting:

```bash
# Format code
black backend/

# Check formatting
black --check backend/

# Lint code
flake8 backend/

# Type checking
mypy backend/

# Import sorting
isort backend/
```

**Configuration files:**
- `pyproject.toml`: Black configuration
- `.flake8`: Flake8 configuration  
- `mypy.ini`: MyPy configuration

#### JavaScript/TypeScript (Frontend)

We use **Prettier** for formatting and **ESLint** for linting:

```bash
cd frontend

# Format code
npm run format

# Check formatting
npm run format:check

# Lint code
npm run lint

# Fix linting issues
npm run lint:fix

# Type checking
npm run type-check
```

**Configuration files:**
- `.prettierrc`: Prettier configuration
- `.eslintrc.json`: ESLint configuration
- `tsconfig.json`: TypeScript configuration

### Pre-commit Hooks

We use **pre-commit** to ensure code quality:

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files

# Update hooks
pre-commit autoupdate
```

**Pre-commit configuration (`.pre-commit-config.yaml`):**
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3.8

  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8

  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort

  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v2.6.2
    hooks:
      - id: prettier
        files: \.(js|jsx|ts|tsx|css|md|json)$
```

## Testing

### Backend Testing

#### Unit Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=api --cov=services --cov=models

# Run specific test file
pytest tests/unit/test_optimization.py

# Run specific test
pytest tests/unit/test_optimization.py::TestQAOA::test_circuit_construction

# Run tests with verbose output
pytest -v

# Run tests and generate HTML coverage report
pytest --cov=api --cov-report=html
```

#### Integration Tests

```bash
# Run integration tests
pytest tests/integration/

# Run API integration tests
pytest tests/integration/test_api_endpoints.py
```

#### Test Structure

```
tests/
├── unit/                           # Unit tests
│   ├── test_optimization.py        # Optimization algorithms
│   ├── test_quantum.py             # Quantum modules
│   ├── test_classical.py           # Classical modules
│   ├── test_models.py              # Data models
│   └── test_services.py            # Business logic
├── integration/                    # Integration tests
│   ├── test_api_endpoints.py       # API endpoint tests
│   ├── test_data_flow.py           # End-to-end data flow
│   └── test_websocket.py           # WebSocket tests
├── fixtures/                       # Test data
│   ├── sample_data.py              # Sample supply chain data
│   └── expected_results.py         # Expected optimization results
└── conftest.py                     # Pytest configuration
```

#### Writing Tests

```python
# tests/unit/test_optimization.py
import pytest
from unittest.mock import Mock, patch
from api.optimization import ClassicalSupplyChainOptimizer

class TestClassicalOptimizer:
    """Test cases for classical optimization algorithms."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.optimizer = ClassicalSupplyChainOptimizer()
        self.sample_warehouses = [
            {
                "id": "w1",
                "name": "Test Warehouse",
                "capacity": 1000,
                "current_inventory": 800
            }
        ]
        self.sample_customers = [
            {
                "id": "c1", 
                "name": "Test Customer",
                "demand": 500,
                "priority": 1
            }
        ]
    
    def test_optimization_success(self):
        """Test successful optimization."""
        result = self.optimizer.optimize_transportation(
            warehouses=self.sample_warehouses,
            customers=self.sample_customers,
            routes=self.sample_routes
        )
        
        assert result["status"] == "success"
        assert result["total_cost"] > 0
        assert len(result["selected_routes"]) > 0
    
    @patch('pulp.LpProblem.solve')
    def test_optimization_failure(self, mock_solve):
        """Test optimization failure handling."""
        mock_solve.return_value = -1  # Infeasible solution
        
        result = self.optimizer.optimize_transportation(
            warehouses=self.sample_warehouses,
            customers=self.sample_customers,
            routes=[]
        )
        
        assert result["status"] == "failed"
```

### Frontend Testing

#### Unit Tests (Jest)

```bash
cd frontend

# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test Dashboard.test.tsx

# Run tests in watch mode
npm test -- --watch
```

#### Component Testing

```typescript
// src/components/__tests__/Dashboard.test.tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { store } from '../store';
import Dashboard from '../Dashboard';

// Mock API calls
jest.mock('../services/api', () => ({
  optimizeSupplyChain: jest.fn()
}));

describe('Dashboard Component', () => {
  beforeEach(() => {
    render(
      <Provider store={store}>
        <Dashboard />
      </Provider>
    );
  });

  it('renders dashboard title', () => {
    expect(
      screen.getByText('Hybrid Quantum-Classical Supply Chain Optimization')
    ).toBeInTheDocument();
  });

  it('handles optimization button click', async () => {
    const optimizeButton = screen.getByText('Run Optimization');
    fireEvent.click(optimizeButton);

    await waitFor(() => {
      expect(screen.getByText('Optimization in progress...')).toBeInTheDocument();
    });
  });

  it('displays optimization results', async () => {
    const mockResult = {
      total_cost: 45000,
      total_co2: 850,
      avg_delivery_time: 8.2
    };

    // Mock API response
    require('../services/api').optimizeSupplyChain.mockResolvedValue(mockResult);

    const optimizeButton = screen.getByText('Run Optimization');
    fireEvent.click(optimizeButton);

    await waitFor(() => {
      expect(screen.getByText('Total Cost: $45,000')).toBeInTheDocument();
      expect(screen.getByText('CO2 Emissions: 850kg')).toBeInTheDocument();
    });
  });
});
```

#### End-to-End Tests (Cypress)

```bash
cd frontend

# Run E2E tests in headless mode
npm run test:e2e

# Run E2E tests with Cypress GUI
npm run test:e2e:open
```

```typescript
// cypress/integration/optimization-flow.spec.ts
describe('Optimization Flow', () => {
  beforeEach(() => {
    cy.visit('/');
    cy.login('test@example.com', 'password');
  });

  it('completes full optimization workflow', () => {
    // Upload data
    cy.get('[data-testid="upload-button"]').click();
    cy.get('[data-testid="file-input"]').selectFile('fixtures/sample-data.csv');
    cy.get('[data-testid="upload-submit"]').click();

    // Verify data upload
    cy.get('[data-testid="data-summary"]').should('contain', '5 Warehouses');
    cy.get('[data-testid="data-summary"]').should('contain', '8 Customers');

    // Run optimization
    cy.get('[data-testid="optimization-method"]').select('hybrid');
    cy.get('[data-testid="run-optimization"]').click();

    // Wait for results
    cy.get('[data-testid="optimization-results"]', { timeout: 30000 })
      .should('be.visible');

    // Verify results
    cy.get('[data-testid="total-cost"]').should('contain', '$');
    cy.get('[data-testid="co2-emissions"]').should('contain', 'kg');
    cy.get('[data-testid="delivery-time"]').should('contain', 'days');

    // Check visualization
    cy.get('[data-testid="map-visualization"]').should('be.visible');
    cy.get('[data-testid="route-lines"]').should('have.length.greaterThan', 0);
  });
});
```

## Debugging

### Backend Debugging

#### Using VS Code

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Flask",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/backend/app.py",
      "env": {
        "FLASK_ENV": "development",
        "FLASK_APP": "app.py"
      },
      "args": [],
      "jinja": true,
      "justMyCode": true
    },
    {
      "name": "Python: Pytest",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["${workspaceFolder}/backend/tests", "-v"],
      "console": "integratedTerminal",
      "justMyCode": true
    }
  ]
}
```

#### Using pdb

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use built-in breakpoint() (Python 3.7+)
breakpoint()
```

#### Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def optimize_routes(self, data):
    logger.debug("Starting route optimization")
    logger.info(f"Processing {len(data['routes'])} routes")
    
    try:
        result = self._run_optimization(data)
        logger.info("Optimization completed successfully")
        return result
    except Exception as e:
        logger.error(f"Optimization failed: {str(e)}")
        raise
```

### Frontend Debugging

#### Browser DevTools

- Use React Developer Tools extension
- Use Redux DevTools extension
- Monitor network requests in Network tab
- Check console for errors and warnings

#### VS Code Debugging

Create `.vscode/launch.json` for frontend:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Launch React App",
      "type": "node",
      "request": "launch",
      "cwd": "${workspaceFolder}/frontend",
      "runtimeExecutable": "npm",
      "runtimeArgs": ["start"]
    },
    {
      "name": "Debug React App",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:3000",
      "webRoot": "${workspaceFolder}/frontend/src"
    }
  ]
}
```

## Database Management

### Migrations

We use Alembic for database migrations:

```bash
cd backend

# Create migration
alembic revision --autogenerate -m "Add new optimization_parameters table"

# Apply migration
alembic upgrade head

# Downgrade migration
alembic downgrade -1

# Show current revision
alembic current

# Show migration history
alembic history
```

### Database Seeding

```bash
cd backend

# Run database seeders
python -m database.seeders.warehouse_seeder
python -m database.seeders.customer_seeder
python -m database.seeders.route_seeder

# Or seed all data
python scripts/seed_database.py
```

### Database Backup/Restore

```bash
# Create backup
pg_dump supply_chain > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
psql supply_chain < backup_20250911_120000.sql

# Using Docker
docker exec -t postgres pg_dump -U postgres supply_chain > backup.sql
docker exec -i postgres psql -U postgres supply_chain < backup.sql
```

## Performance Optimization

### Backend Performance

#### Profiling

```python
# Using cProfile
import cProfile
import pstats

def profile_optimization():
    pr = cProfile.Profile()
    pr.enable()
    
    # Your optimization code here
    result = run_optimization(data)
    
    pr.disable()
    stats = pstats.Stats(pr)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Show top 20 functions

# Using line_profiler
@profile
def optimize_routes(self, data):
    # Function to profile
    pass
```

#### Database Query Optimization

```python
# Use database query logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Optimize queries with eager loading
warehouses = session.query(Warehouse).options(
    joinedload(Warehouse.routes)
).all()

# Use database indexes
class Warehouse(db.Model):
    __tablename__ = 'warehouses'
    
    id = db.Column(db.String, primary_key=True)
    latitude = db.Column(db.Float, index=True)  # Index for geo queries
    longitude = db.Column(db.Float, index=True)
    capacity = db.Column(db.Integer, index=True)  # Index for capacity queries
```

### Frontend Performance

#### Bundle Analysis

```bash
cd frontend

# Analyze bundle size
npm run build
npm install -g webpack-bundle-analyzer
npx webpack-bundle-analyzer build/static/js/*.js
```

#### Code Splitting

```typescript
// Lazy loading components
import { lazy, Suspense } from 'react';

const Dashboard = lazy(() => import('./components/Dashboard'));
const Optimization = lazy(() => import('./components/Optimization'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/optimization" element={<Optimization />} />
      </Routes>
    </Suspense>
  );
}
```

#### Memoization

```typescript
import { memo, useMemo, useCallback } from 'react';

const ExpensiveComponent = memo(({ data, onUpdate }) => {
  const processedData = useMemo(() => {
    return data.map(item => ({
      ...item,
      calculatedValue: expensiveCalculation(item)
    }));
  }, [data]);

  const handleUpdate = useCallback((id, value) => {
    onUpdate(id, value);
  }, [onUpdate]);

  return (
    <div>
      {processedData.map(item => (
        <ItemComponent 
          key={item.id} 
          item={item} 
          onUpdate={handleUpdate} 
        />
      ))}
    </div>
  );
});
```

## Security Best Practices

### Backend Security

1. **Input Validation**
```python
from marshmallow import Schema, fields, validate

class WarehouseSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    latitude = fields.Float(required=True, validate=validate.Range(min=-90, max=90))
    longitude = fields.Float(required=True, validate=validate.Range(min=-180, max=180))
    capacity = fields.Int(required=True, validate=validate.Range(min=1))
```

2. **SQL Injection Prevention**
```python
# Use parameterized queries
cursor.execute(
    "SELECT * FROM warehouses WHERE country = %s AND capacity > %s",
    (country, min_capacity)
)

# Use SQLAlchemy ORM
warehouses = session.query(Warehouse).filter(
    Warehouse.country == country,
    Warehouse.capacity > min_capacity
).all()
```

3. **Authentication & Authorization**
```python
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        verify_jwt_in_request()
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        verify_jwt_in_request()
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return {'error': 'Admin access required'}, 403
        return f(*args, **kwargs)
    return decorated
```

### Frontend Security

1. **XSS Prevention**
```typescript
// Sanitize user input
import DOMPurify from 'dompurify';

const sanitizeInput = (input: string): string => {
  return DOMPurify.sanitize(input);
};

// Use safe innerHTML
<div dangerouslySetInnerHTML={{ __html: sanitizeInput(userContent) }} />
```

2. **CSRF Protection**
```typescript
// Include CSRF token in API requests
const apiClient = axios.create({
  headers: {
    'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content')
  }
});
```

## Deployment

### Local Development Deployment

```bash
# Using Docker Compose
docker-compose -f docker-compose.dev.yml up --build

# Access services
# Frontend: http://localhost:3000
# Backend: http://localhost:5000  
# PostgreSQL: localhost:5432
# Redis: localhost:6379
```

### Production Deployment

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d

# Monitor logs
docker-compose logs -f backend frontend
```

### Environment-Specific Configurations

Create different configuration files for each environment:

- `config/development.py`
- `config/staging.py`  
- `config/production.py`

## Troubleshooting

### Common Issues

#### Backend Issues

1. **Port Already in Use**
```bash
# Find process using port 5000
lsof -i :5000
# Kill process
kill -9 <PID>
```

2. **Database Connection Error**
```bash
# Check PostgreSQL status
brew services list | grep postgresql
# Start PostgreSQL
brew services start postgresql
```

3. **Import Errors**
```bash
# Add project root to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
```

#### Frontend Issues

1. **Node Modules Issues**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

2. **Build Errors**
```bash
# Increase Node memory limit
export NODE_OPTIONS="--max-old-space-size=8192"
npm run build
```

### Debugging Tips

1. **Use proper logging levels**
   - DEBUG: Detailed diagnostic information
   - INFO: General information about program execution
   - WARNING: Something unexpected happened
   - ERROR: Serious problem occurred
   - CRITICAL: Very serious error occurred

2. **Monitor resource usage**
```bash
# Check memory usage
docker stats

# Check disk usage
df -h

# Monitor processes
htop
```

3. **Use health checks**
```bash
# Backend health check
curl http://localhost:5000/api/v1/health

# Database health check
pg_isready -h localhost -p 5432
```

This development guide provides comprehensive instructions for setting up, developing, testing, and maintaining the Hybrid Quantum-Classical Supply Chain Optimization project. Follow these guidelines to ensure consistent, high-quality development practices across the team.