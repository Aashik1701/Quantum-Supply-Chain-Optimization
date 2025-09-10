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
