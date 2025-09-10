"""
Helper functions for optimization algorithms
"""

import numpy as np
from geopy.distance import geodesic
from typing import List, Dict, Any
import uuid
from datetime import datetime


def calculate_distance_matrix(warehouses: List[Dict], customers: List[Dict]) -> np.ndarray:
    """Calculate distance matrix between warehouses and customers"""
    n_warehouses = len(warehouses)
    n_customers = len(customers)
    
    # Initialize distance matrix
    distance_matrix = np.zeros((n_warehouses, n_customers))
    
    for i, warehouse in enumerate(warehouses):
        for j, customer in enumerate(customers):
            # Get coordinates
            warehouse_coords = (warehouse['latitude'], warehouse['longitude'])
            customer_coords = (customer['latitude'], customer['longitude'])
            
            # Calculate geodesic distance in kilometers
            distance = geodesic(warehouse_coords, customer_coords).kilometers
            distance_matrix[i][j] = distance
    
    return distance_matrix


def calculate_route_cost(distance_km: float, cost_per_km: float, fixed_cost: float = 0) -> float:
    """Calculate total route cost"""
    return distance_km * cost_per_km + fixed_cost


def calculate_route_co2(distance_km: float, co2_per_km: float) -> float:
    """Calculate CO2 emissions for a route"""
    return distance_km * co2_per_km


def calculate_delivery_time(distance_km: float, speed_kmh: float, loading_time_hours: float = 2) -> float:
    """Calculate delivery time in hours"""
    travel_time = distance_km / speed_kmh
    return travel_time + loading_time_hours


def format_optimization_result(result: Dict[str, Any], method: str) -> Dict[str, Any]:
    """Format optimization result for API response"""
    formatted_result = {
        'id': str(uuid.uuid4()),
        'method': method,
        'created_at': datetime.utcnow().isoformat(),
        'total_cost': result.get('total_cost', 0),
        'total_co2': result.get('total_co2', 0),
        'avg_delivery_time': result.get('avg_delivery_time', 0),
        'routes_used': result.get('routes_used', 0),
        'routes': result.get('routes', []),
        'assignments': result.get('assignments', []),
        'performance_metrics': {
            'optimization_time_seconds': result.get('optimization_time', 0),
            'iterations': result.get('iterations', 0),
            'convergence': result.get('convergence', False)
        }
    }
    
    # Add method-specific metrics
    if method == 'quantum':
        formatted_result['quantum_metrics'] = {
            'circuit_depth': result.get('circuit_depth', 0),
            'quantum_shots': result.get('quantum_shots', 1024),
            'backend_used': result.get('backend_used', 'simulator')
        }
    
    return formatted_result


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """Validate geographic coordinates"""
    return -90 <= latitude <= 90 and -180 <= longitude <= 180


def calculate_capacity_utilization(assignments: List[Dict], warehouses: List[Dict]) -> Dict[str, float]:
    """Calculate capacity utilization for each warehouse"""
    utilization = {}
    
    # Initialize utilization
    for warehouse in warehouses:
        utilization[warehouse['id']] = 0.0
    
    # Calculate utilization based on assignments
    for assignment in assignments:
        warehouse_id = assignment.get('warehouse_id')
        demand = assignment.get('demand', 0)
        
        if warehouse_id in utilization:
            warehouse = next((w for w in warehouses if w['id'] == warehouse_id), None)
            if warehouse:
                capacity = warehouse.get('capacity', 1)
                utilization[warehouse_id] += demand / capacity
    
    return utilization


def generate_random_coordinates(center_lat: float, center_lon: float, radius_km: float = 100) -> tuple:
    """Generate random coordinates within a radius"""
    # Convert radius to degrees (approximate)
    radius_deg = radius_km / 111  # 1 degree ≈ 111 km
    
    # Generate random offset
    import random
    angle = random.uniform(0, 2 * np.pi)
    distance = random.uniform(0, radius_deg)
    
    lat_offset = distance * np.cos(angle)
    lon_offset = distance * np.sin(angle)
    
    new_lat = center_lat + lat_offset
    new_lon = center_lon + lon_offset
    
    return new_lat, new_lon


def calculate_solution_quality_score(result: Dict[str, Any]) -> float:
    """Calculate overall solution quality score (0-100)"""
    # Weighted scoring based on multiple factors
    cost_score = max(0, 100 - (result.get('total_cost', 0) / 1000))  # Lower cost = higher score
    co2_score = max(0, 100 - (result.get('total_co2', 0) / 10))      # Lower emissions = higher score
    time_score = max(0, 100 - result.get('avg_delivery_time', 0))    # Faster delivery = higher score
    
    # Weighted average
    quality_score = (cost_score * 0.4 + co2_score * 0.3 + time_score * 0.3)
    
    return min(100, max(0, quality_score))


def convert_to_geojson(warehouses: List[Dict], customers: List[Dict], routes: List[Dict] = None) -> Dict:
    """Convert supply chain data to GeoJSON format for mapping"""
    features = []
    
    # Add warehouses
    for warehouse in warehouses:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [warehouse['longitude'], warehouse['latitude']]
            },
            "properties": {
                "type": "warehouse",
                "id": warehouse['id'],
                "name": warehouse['name'],
                "capacity": warehouse.get('capacity', 0)
            }
        })
    
    # Add customers
    for customer in customers:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [customer['longitude'], customer['latitude']]
            },
            "properties": {
                "type": "customer",
                "id": customer['id'],
                "name": customer['name'],
                "demand": customer.get('demand', 0)
            }
        })
    
    # Add routes if provided
    if routes:
        for route in routes:
            # Find warehouse and customer coordinates
            warehouse = next((w for w in warehouses if w['id'] == route.get('warehouse_id')), None)
            customer = next((c for c in customers if c['id'] == route.get('customer_id')), None)
            
            if warehouse and customer:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [warehouse['longitude'], warehouse['latitude']],
                            [customer['longitude'], customer['latitude']]
                        ]
                    },
                    "properties": {
                        "type": "route",
                        "id": route.get('id'),
                        "warehouse_id": route.get('warehouse_id'),
                        "customer_id": route.get('customer_id'),
                        "cost": route.get('total_cost', 0),
                        "co2": route.get('total_co2', 0)
                    }
                })
    
    return {
        "type": "FeatureCollection",
        "features": features
    }
