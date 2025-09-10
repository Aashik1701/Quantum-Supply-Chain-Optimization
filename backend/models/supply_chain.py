"""
Supply chain data models
"""

from typing import List, Optional, Dict, Any
from datetime import datetime


class Warehouse:
    """Warehouse data model"""
    
    def __init__(self, id: str, name: str, latitude: float, longitude: float, 
                 capacity: int, operating_cost: float = 0, country: str = ""):
        self.id = id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.capacity = capacity
        self.operating_cost = operating_cost
        self.country = country
        self.created_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'capacity': self.capacity,
            'operating_cost': self.operating_cost,
            'country': self.country,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Warehouse':
        """Create from dictionary"""
        return cls(
            id=data['id'],
            name=data['name'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            capacity=data['capacity'],
            operating_cost=data.get('operating_cost', 0),
            country=data.get('country', '')
        )


class Customer:
    """Customer data model"""
    
    def __init__(self, id: str, name: str, latitude: float, longitude: float, 
                 demand: int, priority: str = "medium", country: str = ""):
        self.id = id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.demand = demand
        self.priority = priority
        self.country = country
        self.created_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'demand': self.demand,
            'priority': self.priority,
            'country': self.country,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Customer':
        """Create from dictionary"""
        return cls(
            id=data['id'],
            name=data['name'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            demand=data['demand'],
            priority=data.get('priority', 'medium'),
            country=data.get('country', '')
        )


class Route:
    """Route data model"""
    
    def __init__(self, id: str, warehouse_id: str, customer_id: str, 
                 transport_mode: str, cost_per_km: float, co2_per_km: float, 
                 speed_kmh: float, available: bool = True):
        self.id = id
        self.warehouse_id = warehouse_id
        self.customer_id = customer_id
        self.transport_mode = transport_mode
        self.cost_per_km = cost_per_km
        self.co2_per_km = co2_per_km
        self.speed_kmh = speed_kmh
        self.available = available
        self.created_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'warehouse_id': self.warehouse_id,
            'customer_id': self.customer_id,
            'transport_mode': self.transport_mode,
            'cost_per_km': self.cost_per_km,
            'co2_per_km': self.co2_per_km,
            'speed_kmh': self.speed_kmh,
            'available': self.available,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Route':
        """Create from dictionary"""
        return cls(
            id=data['id'],
            warehouse_id=data['warehouse_id'],
            customer_id=data['customer_id'],
            transport_mode=data['transport_mode'],
            cost_per_km=data['cost_per_km'],
            co2_per_km=data['co2_per_km'],
            speed_kmh=data['speed_kmh'],
            available=data.get('available', True)
        )


class OptimizationRequest:
    """Optimization request model"""
    
    def __init__(self, warehouses: List[Warehouse], customers: List[Customer], 
                 routes: Optional[List[Route]] = None, method: str = "hybrid",
                 quantum_params: Optional[Dict[str, Any]] = None):
        self.warehouses = warehouses
        self.customers = customers
        self.routes = routes or []
        self.method = method
        self.quantum_params = quantum_params or {}
        self.created_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'warehouses': [w.to_dict() for w in self.warehouses],
            'customers': [c.to_dict() for c in self.customers],
            'routes': [r.to_dict() for r in self.routes],
            'method': self.method,
            'quantum_params': self.quantum_params,
            'created_at': self.created_at.isoformat()
        }


class OptimizationResult:
    """Optimization result model"""
    
    def __init__(self, id: str, method: str, total_cost: float, total_co2: float, 
                 avg_delivery_time: float, routes_used: int, routes: List[Dict],
                 assignments: List[Dict], optimization_time: float = 0,
                 performance_metrics: Optional[Dict[str, Any]] = None):
        self.id = id
        self.method = method
        self.total_cost = total_cost
        self.total_co2 = total_co2
        self.avg_delivery_time = avg_delivery_time
        self.routes_used = routes_used
        self.routes = routes
        self.assignments = assignments
        self.optimization_time = optimization_time
        self.performance_metrics = performance_metrics or {}
        self.created_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'method': self.method,
            'total_cost': self.total_cost,
            'total_co2': self.total_co2,
            'avg_delivery_time': self.avg_delivery_time,
            'routes_used': self.routes_used,
            'routes': self.routes,
            'assignments': self.assignments,
            'optimization_time': self.optimization_time,
            'performance_metrics': self.performance_metrics,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OptimizationResult':
        """Create from dictionary"""
        return cls(
            id=data['id'],
            method=data['method'],
            total_cost=data['total_cost'],
            total_co2=data['total_co2'],
            avg_delivery_time=data['avg_delivery_time'],
            routes_used=data['routes_used'],
            routes=data['routes'],
            assignments=data['assignments'],
            optimization_time=data.get('optimization_time', 0),
            performance_metrics=data.get('performance_metrics', {})
        )
