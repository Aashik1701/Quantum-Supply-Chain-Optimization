# Sample Data for Hybrid Quantum-Classical Supply Chain Optimization

This directory contains sample datasets for testing and demonstration purposes.

## Files

- `warehouses.csv` - Sample warehouse locations with capacity and operating costs
- `customers.csv` - Sample customer locations with demand and priority levels
- `routes.csv` - Sample transportation routes with different modes and costs

## Data Format

### Warehouses
- `id` - Unique warehouse identifier
- `name` - Human-readable warehouse name
- `latitude` - Geographic latitude coordinate
- `longitude` - Geographic longitude coordinate
- `capacity` - Maximum storage/processing capacity
- `operating_cost` - Daily operating cost in USD
- `country` - Country location

### Customers
- `id` - Unique customer identifier
- `name` - Customer/store name
- `latitude` - Geographic latitude coordinate
- `longitude` - Geographic longitude coordinate
- `demand` - Required delivery quantity
- `priority` - Service priority (high, medium, low)
- `country` - Country location

### Routes (Auto-generated)
Routes are automatically generated based on warehouses and customers with different transportation modes:
- Air freight (fast, expensive, high emissions)
- Sea freight (slow, cheap, low emissions)
- Land transport (medium speed/cost/emissions)

## Usage

Load this data through the web interface or API:

```bash
curl -X POST http://localhost:5000/api/data/upload \
  -F "file=@warehouses.csv" \
  -F "type=warehouses"
```
