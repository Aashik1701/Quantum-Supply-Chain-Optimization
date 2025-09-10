# API Reference Documentation

## Overview

The Hybrid Quantum-Classical Supply Chain Optimization API provides RESTful endpoints for managing supply chain data, running optimization algorithms, and retrieving results. The API supports both synchronous and asynchronous operations with WebSocket support for real-time updates.

**Base URL**: `http://localhost:5000/api/v1`  
**Authentication**: JWT Bearer Token  
**Content-Type**: `application/json`  
**Rate Limiting**: 100 requests per minute per user

## Authentication

### POST /auth/login

Authenticate user and receive JWT token.

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "expires_in": 3600,
    "user": {
      "id": "user_123",
      "username": "user@example.com",
      "role": "user"
    }
  }
}
```

### POST /auth/refresh

Refresh authentication token.

```http
POST /api/v1/auth/refresh
Authorization: Bearer <refresh_token>
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "expires_in": 3600
  }
}
```

### POST /auth/logout

Invalidate authentication token.

```http
POST /api/v1/auth/logout
Authorization: Bearer <access_token>
```

## Data Management

### Warehouses

#### GET /data/warehouses

Retrieve all warehouses.

```http
GET /api/v1/data/warehouses
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page` (integer, optional): Page number for pagination (default: 1)
- `limit` (integer, optional): Items per page (default: 50, max: 100)
- `search` (string, optional): Search by name or city
- `country` (string, optional): Filter by country

**Response:**
```json
{
  "status": "success",
  "data": {
    "warehouses": [
      {
        "id": "w1",
        "name": "New York Hub",
        "city": "New York",
        "country": "USA",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "capacity": 5000,
        "current_inventory": 3200,
        "operating_cost_per_unit": 15.0,
        "created_at": "2025-09-11T00:00:00Z",
        "updated_at": "2025-09-11T00:00:00Z"
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 5,
      "total_items": 25,
      "items_per_page": 50
    }
  }
}
```

#### POST /data/warehouses

Create a new warehouse.

```http
POST /api/v1/data/warehouses
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Chicago Distribution Center",
  "city": "Chicago",
  "country": "USA",
  "latitude": 41.8781,
  "longitude": -87.6298,
  "capacity": 4500,
  "current_inventory": 2800,
  "operating_cost_per_unit": 16.5
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "warehouse": {
      "id": "w6",
      "name": "Chicago Distribution Center",
      "city": "Chicago",
      "country": "USA",
      "latitude": 41.8781,
      "longitude": -87.6298,
      "capacity": 4500,
      "current_inventory": 2800,
      "operating_cost_per_unit": 16.5,
      "created_at": "2025-09-11T12:00:00Z",
      "updated_at": "2025-09-11T12:00:00Z"
    }
  }
}
```

#### PUT /data/warehouses/{id}

Update an existing warehouse.

```http
PUT /api/v1/data/warehouses/w6
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "capacity": 5000,
  "current_inventory": 3500,
  "operating_cost_per_unit": 15.8
}
```

#### DELETE /data/warehouses/{id}

Delete a warehouse.

```http
DELETE /api/v1/data/warehouses/w6
Authorization: Bearer <access_token>
```

### Customers

#### GET /data/customers

Retrieve all customers.

```http
GET /api/v1/data/customers
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page` (integer, optional): Page number for pagination
- `limit` (integer, optional): Items per page
- `search` (string, optional): Search by name or city
- `priority` (integer, optional): Filter by priority level (1-3)

**Response:**
```json
{
  "status": "success",
  "data": {
    "customers": [
      {
        "id": "c1",
        "name": "London Store",
        "city": "London",
        "country": "UK",
        "latitude": 51.5074,
        "longitude": -0.1278,
        "demand": 800,
        "priority": 1,
        "max_delivery_time_days": 7,
        "created_at": "2025-09-11T00:00:00Z",
        "updated_at": "2025-09-11T00:00:00Z"
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 3,
      "total_items": 15,
      "items_per_page": 50
    }
  }
}
```

#### POST /data/customers

Create a new customer.

```http
POST /api/v1/data/customers
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Paris Retail",
  "city": "Paris",
  "country": "France",
  "latitude": 48.8566,
  "longitude": 2.3522,
  "demand": 650,
  "priority": 2,
  "max_delivery_time_days": 8
}
```

### Routes

#### GET /data/routes

Retrieve all routes with filtering options.

```http
GET /api/v1/data/routes?warehouse_id=w1&customer_id=c1&transport_mode=Air
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `warehouse_id` (string, optional): Filter by warehouse
- `customer_id` (string, optional): Filter by customer
- `transport_mode` (string, optional): Filter by transport mode
- `max_cost` (float, optional): Maximum cost per unit
- `max_delivery_time` (float, optional): Maximum delivery time in days

**Response:**
```json
{
  "status": "success",
  "data": {
    "routes": [
      {
        "id": "r1",
        "warehouse_id": "w1",
        "customer_id": "c1",
        "transport_mode": "Air",
        "distance_km": 5570.22,
        "cost_per_unit": 1392.56,
        "delivery_time_days": 0.70,
        "co2_per_unit": 0.45,
        "capacity_limit": 2000,
        "reliability": 0.95
      }
    ]
  }
}
```

### Data Upload

#### POST /data/upload

Upload CSV files for batch data import.

```http
POST /api/v1/data/upload
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

Form Data:
- file: <CSV file>
- data_type: "warehouses|customers|routes"
- validate_only: false (boolean, optional)
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "upload_id": "upload_123",
    "data_type": "warehouses",
    "total_records": 25,
    "valid_records": 23,
    "invalid_records": 2,
    "errors": [
      {
        "row": 5,
        "field": "latitude",
        "message": "Invalid latitude value"
      },
      {
        "row": 12,
        "field": "capacity",
        "message": "Capacity must be a positive integer"
      }
    ],
    "preview": [
      {
        "name": "Seattle Hub",
        "city": "Seattle",
        "country": "USA",
        "latitude": 47.6062,
        "longitude": -122.3321,
        "capacity": 3800
      }
    ]
  }
}
```

## Optimization Endpoints

### Classical Optimization

#### POST /optimization/classical

Run classical linear programming optimization.

```http
POST /api/v1/optimization/classical
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "warehouses": [
    {
      "id": "w1",
      "name": "New York Hub",
      "capacity": 5000,
      "current_inventory": 3200
    }
  ],
  "customers": [
    {
      "id": "c1",
      "name": "London Store",
      "demand": 800,
      "priority": 1
    }
  ],
  "routes": [
    {
      "warehouse_id": "w1",
      "customer_id": "c1",
      "transport_mode": "Air",
      "cost_per_unit": 1392.56,
      "delivery_time_days": 0.70,
      "co2_per_unit": 0.45
    }
  ],
  "parameters": {
    "solver": "CBC",
    "time_limit": 300,
    "gap_tolerance": 0.01,
    "objective_weights": {
      "cost": 0.6,
      "co2": 0.25,
      "time": 0.15
    }
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "job_id": "opt_classical_123",
    "method": "classical",
    "solver_status": "optimal",
    "total_cost": 45000.00,
    "total_co2": 850.5,
    "avg_delivery_time": 8.2,
    "routes_used": 12,
    "selected_routes": [
      {
        "warehouse_id": "w1",
        "customer_id": "c1",
        "quantity": 800,
        "transport_mode": "Air",
        "cost": 1114048.00,
        "co2_emission": 360.0,
        "delivery_time": 0.70
      }
    ],
    "execution_time": 2.45,
    "iterations": 156,
    "created_at": "2025-09-11T12:00:00Z"
  }
}
```

### Quantum Optimization

#### POST /optimization/quantum

Run QAOA quantum optimization.

```http
POST /api/v1/optimization/quantum
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "warehouses": [...],
  "customers": [...],
  "routes": [...],
  "parameters": {
    "reps": 3,
    "optimizer": "COBYLA",
    "max_iterations": 200,
    "initial_params": "random",
    "backend": "qasm_simulator",
    "shots": 1024,
    "noise_model": null,
    "constraint_penalty": 1000.0
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "job_id": "opt_quantum_456",
    "method": "quantum_qaoa",
    "total_cost": 42300.00,
    "total_co2": 720.8,
    "avg_delivery_time": 7.8,
    "routes_used": 10,
    "selected_routes": [...],
    "quantum_metrics": {
      "circuit_depth": 15,
      "gate_count": 234,
      "optimization_iterations": 89,
      "final_eigenvalue": -42300.00,
      "convergence_reached": true
    },
    "execution_time": 15.67,
    "created_at": "2025-09-11T12:05:00Z"
  }
}
```

### Hybrid Optimization

#### POST /optimization/hybrid

Run hybrid quantum-classical optimization.

```http
POST /api/v1/optimization/hybrid
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "warehouses": [...],
  "customers": [...],
  "routes": [...],
  "parameters": {
    "classical_preprocessor": true,
    "quantum_refinement": true,
    "classical_params": {
      "solver": "CBC",
      "time_limit": 120
    },
    "quantum_params": {
      "reps": 2,
      "optimizer": "SPSA",
      "max_iterations": 100
    },
    "integration_strategy": "sequential",
    "improvement_threshold": 0.05
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "job_id": "opt_hybrid_789",
    "method": "hybrid",
    "total_cost": 38500.00,
    "total_co2": 720.0,
    "avg_delivery_time": 7.1,
    "routes_used": 9,
    "selected_routes": [...],
    "classical_result": {
      "cost": 45000.00,
      "execution_time": 1.23
    },
    "quantum_result": {
      "cost": 42300.00,
      "execution_time": 12.45
    },
    "hybrid_improvement": {
      "cost_improvement": 14.4,
      "co2_improvement": 15.3,
      "time_improvement": 13.4
    },
    "execution_time": 18.92,
    "created_at": "2025-09-11T12:10:00Z"
  }
}
```

### Optimization Status

#### GET /optimization/jobs/{job_id}

Get optimization job status and results.

```http
GET /api/v1/optimization/jobs/opt_hybrid_789
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "job_id": "opt_hybrid_789",
    "status": "completed",
    "method": "hybrid",
    "progress": 100,
    "created_at": "2025-09-11T12:10:00Z",
    "started_at": "2025-09-11T12:10:05Z",
    "completed_at": "2025-09-11T12:10:24Z",
    "execution_time": 18.92,
    "result": {
      "total_cost": 38500.00,
      "total_co2": 720.0,
      "avg_delivery_time": 7.1,
      "routes_used": 9,
      "selected_routes": [...]
    }
  }
}
```

#### GET /optimization/jobs

List optimization jobs with filtering.

```http
GET /api/v1/optimization/jobs?status=completed&method=hybrid&limit=20
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `status` (string, optional): Filter by status (pending|running|completed|failed)
- `method` (string, optional): Filter by method (classical|quantum|hybrid)
- `user_id` (string, optional): Filter by user ID
- `created_after` (ISO date, optional): Jobs created after date
- `limit` (integer, optional): Number of results (default: 50)

### Cancel Optimization

#### POST /optimization/jobs/{job_id}/cancel

Cancel a running optimization job.

```http
POST /api/v1/optimization/jobs/opt_hybrid_789/cancel
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "job_id": "opt_hybrid_789",
    "status": "cancelled",
    "message": "Optimization job cancelled successfully"
  }
}
```

## Results and Analytics

### Comparison

#### POST /results/compare

Compare multiple optimization results.

```http
POST /api/v1/results/compare
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "job_ids": ["opt_classical_123", "opt_quantum_456", "opt_hybrid_789"],
  "metrics": ["total_cost", "total_co2", "avg_delivery_time", "routes_used"],
  "normalization": "percentage"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "comparison": {
      "total_cost": {
        "opt_classical_123": 45000.00,
        "opt_quantum_456": 42300.00,
        "opt_hybrid_789": 38500.00,
        "best": "opt_hybrid_789",
        "improvement": 14.4
      },
      "total_co2": {
        "opt_classical_123": 850.5,
        "opt_quantum_456": 720.8,
        "opt_hybrid_789": 720.0,
        "best": "opt_hybrid_789",
        "improvement": 15.3
      },
      "avg_delivery_time": {
        "opt_classical_123": 8.2,
        "opt_quantum_456": 7.8,
        "opt_hybrid_789": 7.1,
        "best": "opt_hybrid_789",
        "improvement": 13.4
      }
    },
    "summary": {
      "best_overall": "opt_hybrid_789",
      "total_improvement": 14.37
    }
  }
}
```

### Export Results

#### GET /results/{job_id}/export

Export optimization results in various formats.

```http
GET /api/v1/results/opt_hybrid_789/export?format=csv&include_metadata=true
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `format` (string): Export format (csv|json|xlsx|pdf)
- `include_metadata` (boolean, optional): Include job metadata
- `include_routes` (boolean, optional): Include detailed route information

**Response:** File download with appropriate Content-Type header.

## System Information

### Health Check

#### GET /health

System health check (no authentication required).

```http
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-11T12:00:00Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "cache": "healthy",
    "quantum_service": "healthy",
    "message_queue": "healthy"
  },
  "performance": {
    "response_time_ms": 45,
    "cpu_usage": 25.6,
    "memory_usage": 68.2,
    "active_connections": 23
  }
}
```

### System Status

#### GET /system/status

Detailed system status (admin only).

```http
GET /api/v1/system/status
Authorization: Bearer <admin_access_token>
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "system": {
      "uptime": "5 days, 14 hours, 32 minutes",
      "version": "1.0.0",
      "environment": "production"
    },
    "quantum": {
      "backend_status": "available",
      "queue_length": 0,
      "avg_execution_time": 12.5,
      "success_rate": 97.8
    },
    "classical": {
      "solver_status": "available",
      "avg_execution_time": 2.1,
      "success_rate": 99.9
    },
    "database": {
      "connections": 15,
      "slow_queries": 2,
      "storage_used": "2.3 GB",
      "last_backup": "2025-09-11T06:00:00Z"
    }
  }
}
```

## WebSocket Events

### Connection

```javascript
const socket = io('ws://localhost:5000/socket.io', {
  auth: {
    token: 'Bearer <access_token>'
  }
});

socket.on('connect', () => {
  console.log('Connected to WebSocket server');
});
```

### Optimization Progress

```javascript
socket.on('optimization_progress', (data) => {
  console.log('Optimization progress:', data);
  // {
  //   job_id: 'opt_hybrid_789',
  //   progress: 65,
  //   current_step: 'quantum_optimization',
  //   estimated_remaining: 45
  // }
});

socket.on('optimization_complete', (data) => {
  console.log('Optimization completed:', data);
  // {
  //   job_id: 'opt_hybrid_789',
  //   status: 'completed',
  //   result: { ... }
  // }
});

socket.on('optimization_error', (data) => {
  console.error('Optimization error:', data);
  // {
  //   job_id: 'opt_hybrid_789',
  //   error: 'Quantum circuit execution failed',
  //   details: '...'
  // }
});
```

## Error Codes

| Code | Message | Description |
|------|---------|-------------|
| 400 | Bad Request | Invalid request format or parameters |
| 401 | Unauthorized | Authentication required or invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource already exists or constraint violation |
| 422 | Unprocessable Entity | Validation errors |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 502 | Bad Gateway | Quantum service unavailable |
| 503 | Service Unavailable | Maintenance mode |

### Error Response Format

```json
{
  "status": "error",
  "error": {
    "code": 422,
    "message": "Validation error",
    "details": [
      {
        "field": "warehouses.0.capacity",
        "message": "Capacity must be greater than 0"
      },
      {
        "field": "customers.2.demand",
        "message": "Demand is required"
      }
    ],
    "timestamp": "2025-09-11T12:00:00Z",
    "request_id": "req_abc123"
  }
}
```

## Rate Limiting

| Endpoint Pattern | Limit | Window |
|------------------|-------|---------|
| `/auth/*` | 10 requests | 1 minute |
| `/optimization/*` | 5 requests | 5 minutes |
| `/data/*` (GET) | 100 requests | 1 minute |
| `/data/*` (POST/PUT/DELETE) | 20 requests | 1 minute |
| `/health` | Unlimited | - |

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Request limit per window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Window reset time (Unix timestamp)

## SDK Examples

### Python SDK

```python
from supply_chain_optimizer import OptimizationClient

# Initialize client
client = OptimizationClient(
    api_url="http://localhost:5000/api/v1",
    access_token="your_access_token"
)

# Run optimization
result = client.optimize(
    method="hybrid",
    warehouses=warehouses_data,
    customers=customers_data,
    routes=routes_data,
    parameters={
        "quantum_params": {"reps": 3},
        "classical_params": {"solver": "CBC"}
    }
)

print(f"Total cost: ${result.total_cost}")
print(f"CO2 emissions: {result.total_co2}kg")
```

### JavaScript SDK

```javascript
import { SupplyChainAPI } from '@supply-chain/api-client';

const api = new SupplyChainAPI({
  baseUrl: 'http://localhost:5000/api/v1',
  accessToken: 'your_access_token'
});

// Run optimization
const result = await api.optimization.hybrid({
  warehouses: warehousesData,
  customers: customersData,
  routes: routesData,
  parameters: {
    quantumParams: { reps: 3 },
    classicalParams: { solver: 'CBC' }
  }
});

console.log(`Total cost: $${result.totalCost}`);
console.log(`CO2 emissions: ${result.totalCo2}kg`);
```

This API reference provides comprehensive documentation for all available endpoints, request/response formats, authentication, error handling, and rate limiting for the Hybrid Quantum-Classical Supply Chain Optimization platform.