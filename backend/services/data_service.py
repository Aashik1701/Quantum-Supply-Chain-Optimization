"""
Data management service
"""

import json
from typing import Dict, List, Any
import os

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from werkzeug.utils import secure_filename
    WERKZEUG_AVAILABLE = True
except ImportError:
    WERKZEUG_AVAILABLE = False
    def secure_filename(filename):
        return filename


class DataService:
    """Service for managing supply chain data"""
    
    def __init__(self):
        self.warehouses = []
        self.customers = []
        self.routes = []
        self._load_sample_data()
    
    def _load_sample_data(self):
        """Load sample data for testing"""
        # Sample warehouses
        self.warehouses = [
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
            },
            {
                "id": "W3",
                "name": "Singapore Hub",
                "latitude": 1.3521,
                "longitude": 103.8198,
                "capacity": 3500,
                "operating_cost": 900,
                "country": "Singapore"
            }
        ]
        
        # Sample customers
        self.customers = [
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
            },
            {
                "id": "C3",
                "name": "Sydney Outlet",
                "latitude": -33.8688,
                "longitude": 151.2093,
                "demand": 600,
                "priority": "low",
                "country": "Australia"
            },
            {
                "id": "C4",
                "name": "Berlin Branch",
                "latitude": 52.5200,
                "longitude": 13.4050,
                "demand": 900,
                "priority": "high",
                "country": "Germany"
            }
        ]
        
        # Sample routes (generated dynamically based on warehouses and customers)
        self.routes = self._generate_sample_routes()
    
    def _generate_sample_routes(self):
        """Generate sample routes between warehouses and customers"""
        routes = []
        transport_modes = [
            {"type": "air", "cost_per_km": 2.5, "co2_per_km": 0.8, "speed_kmh": 800},
            {"type": "sea", "cost_per_km": 0.5, "co2_per_km": 0.2, "speed_kmh": 50},
            {"type": "land", "cost_per_km": 1.0, "co2_per_km": 0.4, "speed_kmh": 80}
        ]
        
        for warehouse in self.warehouses:
            for customer in self.customers:
                for transport in transport_modes:
                    route_id = f"{warehouse['id']}-{customer['id']}-{transport['type']}"
                    routes.append({
                        "id": route_id,
                        "warehouse_id": warehouse["id"],
                        "customer_id": customer["id"],
                        "transport_mode": transport["type"],
                        "cost_per_km": transport["cost_per_km"],
                        "co2_per_km": transport["co2_per_km"],
                        "speed_kmh": transport["speed_kmh"],
                        "available": True
                    })
        
        return routes
    
    def get_warehouses(self) -> List[Dict[str, Any]]:
        """Get all warehouses"""
        return self.warehouses
    
    def get_customers(self) -> List[Dict[str, Any]]:
        """Get all customers"""
        return self.customers
    
    def get_routes(self) -> List[Dict[str, Any]]:
        """Get all routes"""
        return self.routes
    
    def create_warehouse(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new warehouse"""
        warehouse = {
            "id": data.get("id") or f"W{len(self.warehouses) + 1}",
            "name": data.get("name"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "capacity": data.get("capacity", 1000),
            "operating_cost": data.get("operating_cost", 500),
            "country": data.get("country", "Unknown")
        }
        self.warehouses.append(warehouse)
        return warehouse
    
    def create_customer(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new customer"""
        customer = {
            "id": data.get("id") or f"C{len(self.customers) + 1}",
            "name": data.get("name"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "demand": data.get("demand", 100),
            "priority": data.get("priority", "medium"),
            "country": data.get("country", "Unknown")
        }
        self.customers.append(customer)
        return customer
    
    def create_route(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new route"""
        route = {
            "id": data.get("id") or f"R{len(self.routes) + 1}",
            "warehouse_id": data.get("warehouse_id"),
            "customer_id": data.get("customer_id"),
            "transport_mode": data.get("transport_mode", "land"),
            "cost_per_km": data.get("cost_per_km", 1.0),
            "co2_per_km": data.get("co2_per_km", 0.4),
            "speed_kmh": data.get("speed_kmh", 80),
            "available": data.get("available", True)
        }
        self.routes.append(route)
        return route
    
    def process_upload(self, file, data_type: str) -> Dict[str, Any]:
        """Process uploaded CSV file"""
        try:
            # Secure filename
            filename = secure_filename(file.filename) if WERKZEUG_AVAILABLE else file.filename
            
            if not PANDAS_AVAILABLE:
                return {"error": "Pandas not available for CSV processing"}, 500
            
            # Read CSV
            df = pd.read_csv(file)
            
            # Convert to records
            records = df.to_dict('records')
            
            # Process based on data type
            if data_type == 'warehouses':
                self.warehouses.extend(records)
                return {"message": f"Added {len(records)} warehouses", "count": len(records)}
            
            elif data_type == 'customers':
                self.customers.extend(records)
                return {"message": f"Added {len(records)} customers", "count": len(records)}
            
            elif data_type == 'routes':
                self.routes.extend(records)
                return {"message": f"Added {len(records)} routes", "count": len(records)}
            
            else:
                return {"error": "Invalid data type"}, 400
                
        except Exception as e:
            return {"error": f"Failed to process upload: {str(e)}"}, 500
    
    def get_sample_data(self) -> Dict[str, Any]:
        """Get complete sample dataset"""
        return {
            "warehouses": self.warehouses,
            "customers": self.customers,
            "routes": self.routes,
            "metadata": {
                "warehouse_count": len(self.warehouses),
                "customer_count": len(self.customers),
                "route_count": len(self.routes)
            }
        }

    def validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate supply chain data for completeness and consistency"""
        errors = []
        warnings = []
        details = {}
        
        # Extract data components
        warehouses = data.get('warehouses', [])
        customers = data.get('customers', [])
        routes = data.get('routes', [])
        
        # Validate warehouses
        if warehouses:
            warehouse_errors, warehouse_warnings = self._validate_warehouses(warehouses)
            errors.extend(warehouse_errors)
            warnings.extend(warehouse_warnings)
            details['warehouses'] = {
                'count': len(warehouses),
                'valid_ids': [w.get('id') for w in warehouses if w.get('id')],
                'capacity_range': self._get_capacity_range(warehouses)
            }
        else:
            warnings.append("No warehouse data provided")
        
        # Validate customers
        if customers:
            customer_errors, customer_warnings = self._validate_customers(customers)
            errors.extend(customer_errors)
            warnings.extend(customer_warnings)
            details['customers'] = {
                'count': len(customers),
                'valid_ids': [c.get('id') for c in customers if c.get('id')],
                'demand_range': self._get_demand_range(customers)
            }
        else:
            warnings.append("No customer data provided")
        
        # Validate routes
        if routes:
            route_errors, route_warnings = self._validate_routes(routes, warehouses, customers)
            errors.extend(route_errors)
            warnings.extend(route_warnings)
            details['routes'] = {
                'count': len(routes),
                'transport_modes': list(set(r.get('transport_mode', 'unknown') for r in routes))
            }
        else:
            warnings.append("No route data provided")
        
        # Check data consistency
        if warehouses and customers and routes:
            consistency_errors = self._validate_consistency(warehouses, customers, routes)
            errors.extend(consistency_errors)
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'details': details
        }

    def _validate_warehouses(self, warehouses: List[Dict]) -> tuple:
        """Validate warehouse data"""
        errors = []
        warnings = []
        
        required_fields = ['id', 'latitude', 'longitude', 'capacity']
        
        for i, warehouse in enumerate(warehouses):
            # Check required fields
            for field in required_fields:
                if field not in warehouse or warehouse[field] is None:
                    errors.append(f"Warehouse {i+1}: Missing required field '{field}'")
            
            # Validate coordinates
            if 'latitude' in warehouse and warehouse['latitude']:
                lat = warehouse['latitude']
                if not isinstance(lat, (int, float)) or lat < -90 or lat > 90:
                    errors.append(f"Warehouse {i+1}: Invalid latitude {lat}")
            
            if 'longitude' in warehouse and warehouse['longitude']:
                lng = warehouse['longitude']
                if not isinstance(lng, (int, float)) or lng < -180 or lng > 180:
                    errors.append(f"Warehouse {i+1}: Invalid longitude {lng}")
            
            # Validate capacity
            if 'capacity' in warehouse and warehouse['capacity']:
                capacity = warehouse['capacity']
                if not isinstance(capacity, (int, float)) or capacity <= 0:
                    errors.append(f"Warehouse {i+1}: Invalid capacity {capacity}")
        
        return errors, warnings

    def _validate_customers(self, customers: List[Dict]) -> tuple:
        """Validate customer data"""
        errors = []
        warnings = []
        
        required_fields = ['id', 'latitude', 'longitude', 'demand']
        
        for i, customer in enumerate(customers):
            # Check required fields
            for field in required_fields:
                if field not in customer or customer[field] is None:
                    errors.append(f"Customer {i+1}: Missing required field '{field}'")
            
            # Validate coordinates
            if 'latitude' in customer and customer['latitude']:
                lat = customer['latitude']
                if not isinstance(lat, (int, float)) or lat < -90 or lat > 90:
                    errors.append(f"Customer {i+1}: Invalid latitude {lat}")
            
            if 'longitude' in customer and customer['longitude']:
                lng = customer['longitude']
                if not isinstance(lng, (int, float)) or lng < -180 or lng > 180:
                    errors.append(f"Customer {i+1}: Invalid longitude {lng}")
            
            # Validate demand
            if 'demand' in customer and customer['demand']:
                demand = customer['demand']
                if not isinstance(demand, (int, float)) or demand <= 0:
                    errors.append(f"Customer {i+1}: Invalid demand {demand}")
        
        return errors, warnings

    def _validate_routes(self, routes: List[Dict], warehouses: List[Dict], customers: List[Dict]) -> tuple:
        """Validate route data"""
        errors = []
        warnings = []
        
        warehouse_ids = set(w.get('id') for w in warehouses if w.get('id'))
        customer_ids = set(c.get('id') for c in customers if c.get('id'))
        
        required_fields = ['origin_id', 'destination_id', 'distance', 'cost']
        
        for i, route in enumerate(routes):
            # Check required fields
            for field in required_fields:
                if field not in route or route[field] is None:
                    errors.append(f"Route {i+1}: Missing required field '{field}'")
            
            # Validate origin and destination references
            if 'origin_id' in route and route['origin_id']:
                if route['origin_id'] not in warehouse_ids:
                    errors.append(f"Route {i+1}: Origin ID '{route['origin_id']}' not found in warehouses")
            
            if 'destination_id' in route and route['destination_id']:
                if route['destination_id'] not in customer_ids:
                    errors.append(f"Route {i+1}: Destination ID '{route['destination_id']}' not found in customers")
            
            # Validate distance and cost
            if 'distance' in route and route['distance']:
                distance = route['distance']
                if not isinstance(distance, (int, float)) or distance <= 0:
                    errors.append(f"Route {i+1}: Invalid distance {distance}")
            
            if 'cost' in route and route['cost']:
                cost = route['cost']
                if not isinstance(cost, (int, float)) or cost < 0:
                    errors.append(f"Route {i+1}: Invalid cost {cost}")
        
        return errors, warnings

    def _validate_consistency(self, warehouses: List[Dict], customers: List[Dict], routes: List[Dict]) -> List[str]:
        """Validate consistency between different data types"""
        errors = []
        
        # Check if total warehouse capacity can meet total customer demand
        total_capacity = sum(w.get('capacity', 0) for w in warehouses)
        total_demand = sum(c.get('demand', 0) for c in customers)
        
        if total_capacity < total_demand:
            errors.append(f"Total warehouse capacity ({total_capacity}) insufficient for total demand ({total_demand})")
        
        return errors

    def _get_capacity_range(self, warehouses: List[Dict]) -> Dict[str, float]:
        """Get capacity range for warehouses"""
        capacities = [w.get('capacity', 0) for w in warehouses if w.get('capacity')]
        if capacities:
            return {'min': min(capacities), 'max': max(capacities), 'total': sum(capacities)}
        return {'min': 0, 'max': 0, 'total': 0}

    def _get_demand_range(self, customers: List[Dict]) -> Dict[str, float]:
        """Get demand range for customers"""
        demands = [c.get('demand', 0) for c in customers if c.get('demand')]
        if demands:
            return {'min': min(demands), 'max': max(demands), 'total': sum(demands)}
        return {'min': 0, 'max': 0, 'total': 0}

    def delete_data(self, data_type: str) -> Dict[str, Any]:
        """Delete specific data type"""
        if data_type == 'warehouses':
            count = len(self.warehouses)
            self.warehouses = []
            return {'message': f'Deleted {count} warehouses', 'count': 0}
        elif data_type == 'customers':
            count = len(self.customers)
            self.customers = []
            return {'message': f'Deleted {count} customers', 'count': 0}
        elif data_type == 'routes':
            count = len(self.routes)
            self.routes = []
            return {'message': f'Deleted {count} routes', 'count': 0}
        else:
            return {'error': 'Invalid data type'}
