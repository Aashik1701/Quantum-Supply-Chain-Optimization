"""
Input validation utilities
"""

from typing import Dict, Any, List


def validate_optimization_request(data: Dict[str, Any]) -> bool:
    """Validate optimization request data"""
    if not isinstance(data, dict):
        return False
    
    # Check required fields
    if 'warehouses' not in data or 'customers' not in data:
        return False
    
    warehouses = data['warehouses']
    customers = data['customers']
    
    # Validate warehouses
    if not isinstance(warehouses, list) or len(warehouses) == 0:
        return False
    
    for warehouse in warehouses:
        if not validate_warehouse(warehouse):
            return False
    
    # Validate customers
    if not isinstance(customers, list) or len(customers) == 0:
        return False
    
    for customer in customers:
        if not validate_customer(customer):
            return False
    
    return True


def validate_warehouse(warehouse: Dict[str, Any]) -> bool:
    """Validate warehouse data"""
    required_fields = ['id', 'name', 'latitude', 'longitude', 'capacity']
    
    for field in required_fields:
        if field not in warehouse:
            return False
    
    # Validate coordinates
    lat = warehouse['latitude']
    lon = warehouse['longitude']
    
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
        return False
    
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        return False
    
    # Validate capacity
    capacity = warehouse['capacity']
    if not isinstance(capacity, (int, float)) or capacity <= 0:
        return False
    
    return True


def validate_customer(customer: Dict[str, Any]) -> bool:
    """Validate customer data"""
    required_fields = ['id', 'name', 'latitude', 'longitude', 'demand']
    
    for field in required_fields:
        if field not in customer:
            return False
    
    # Validate coordinates
    lat = customer['latitude']
    lon = customer['longitude']
    
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
        return False
    
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        return False
    
    # Validate demand
    demand = customer['demand']
    if not isinstance(demand, (int, float)) or demand <= 0:
        return False
    
    return True


def validate_route(route: Dict[str, Any]) -> bool:
    """Validate route data"""
    required_fields = ['warehouse_id', 'customer_id', 'transport_mode']
    
    for field in required_fields:
        if field not in route:
            return False
    
    # Validate transport mode
    valid_modes = ['air', 'sea', 'land', 'rail']
    if route['transport_mode'] not in valid_modes:
        return False
    
    # Validate optional numeric fields
    numeric_fields = ['cost_per_km', 'co2_per_km', 'speed_kmh']
    for field in numeric_fields:
        if field in route:
            value = route[field]
            if not isinstance(value, (int, float)) or value < 0:
                return False
    
    return True


def validate_quantum_parameters(params: Dict[str, Any]) -> bool:
    """Validate quantum optimization parameters"""
    if not isinstance(params, dict):
        return True  # Optional parameters
    
    # Validate shots
    if 'shots' in params:
        shots = params['shots']
        if not isinstance(shots, int) or shots <= 0 or shots > 100000:
            return False
    
    # Validate p_layers
    if 'p_layers' in params:
        p_layers = params['p_layers']
        if not isinstance(p_layers, int) or p_layers <= 0 or p_layers > 10:
            return False
    
    # Validate backend
    if 'backend' in params:
        backend = params['backend']
        valid_backends = ['qasm_simulator', 'statevector_simulator', 'ibm_quantum']
        if backend not in valid_backends:
            return False
    
    return True


def sanitize_string(input_string: str, max_length: int = 100) -> str:
    """Sanitize string input"""
    if not isinstance(input_string, str):
        return ""
    
    # Remove potentially harmful characters
    sanitized = input_string.strip()
    sanitized = ''.join(char for char in sanitized if char.isprintable())
    
    # Truncate to max length
    return sanitized[:max_length]


def validate_file_upload(filename: str, allowed_extensions: set) -> bool:
    """Validate file upload"""
    if not filename:
        return False
    
    # Check extension
    if '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in allowed_extensions
