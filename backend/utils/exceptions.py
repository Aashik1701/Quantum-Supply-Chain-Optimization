"""
Domain-specific exception classes for supply chain optimization
"""

from typing import Optional, Dict, Any


class SupplyChainError(Exception):
    """Base exception for all supply chain optimization errors"""

    def __init__(
        self,
        message: str,
        code: str = "UNKNOWN_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(SupplyChainError):
    """Raised when data validation fails"""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code="VALIDATION_ERROR", details=details)


class OptimizationError(SupplyChainError):
    """Raised when optimization process fails"""

    def __init__(
        self,
        message: str,
        method: str = "unknown",
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details["method"] = method
        super().__init__(message, code="OPTIMIZATION_ERROR", details=details)


class DataNotFoundError(SupplyChainError):
    """Raised when requested data is not found"""

    def __init__(
        self,
        resource: str,
        identifier: str = "",
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"{resource} not found"
        if identifier:
            message += f": {identifier}"
        details = details or {}
        details["resource"] = resource
        details["identifier"] = identifier
        super().__init__(message, code="NOT_FOUND", details=details)


class ConfigurationError(SupplyChainError):
    """Raised when configuration is invalid or missing"""

    def __init__(
        self,
        message: str,
        config_key: str = "",
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if config_key:
            details["config_key"] = config_key
        super().__init__(message, code="CONFIGURATION_ERROR", details=details)


class CapacityError(SupplyChainError):
    """Raised when capacity constraints are violated"""

    def __init__(
        self,
        message: str,
        resource_type: str = "",
        capacity: float = 0,
        demand: float = 0
    ):
        details = {
            "resource_type": resource_type,
            "capacity": capacity,
            "demand": demand,
            "overflow": demand - capacity if capacity > 0 else 0
        }
        super().__init__(message, code="CAPACITY_EXCEEDED", details=details)


class RouteError(SupplyChainError):
    """Raised when route calculation or validation fails"""

    def __init__(
        self,
        message: str,
        origin: str = "",
        destination: str = "",
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details.update({
            "origin": origin,
            "destination": destination
        })
        super().__init__(message, code="ROUTE_ERROR", details=details)


class QuantumError(SupplyChainError):
    """Raised when quantum computation fails"""

    def __init__(
        self,
        message: str,
        backend: str = "",
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details["backend"] = backend
        super().__init__(message, code="QUANTUM_ERROR", details=details)


class AuthenticationError(SupplyChainError):
    """Raised when authentication fails"""

    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code="AUTHENTICATION_ERROR", details=details)


class AuthorizationError(SupplyChainError):
    """Raised when authorization fails"""

    def __init__(
        self,
        message: str = "Access denied",
        resource: str = "",
        action: str = ""
    ):
        details = {
            "resource": resource,
            "action": action
        }
        super().__init__(message, code="AUTHORIZATION_ERROR", details=details)


class RateLimitError(SupplyChainError):
    """Raised when rate limit is exceeded"""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        limit: int = 0,
        window: str = ""
    ):
        details = {
            "limit": limit,
            "window": window
        }
        super().__init__(message, code="RATE_LIMIT_EXCEEDED", details=details)


class ExternalServiceError(SupplyChainError):
    """Raised when external service call fails"""

    def __init__(
        self,
        message: str,
        service: str = "",
        status_code: int = 0,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details.update({
            "service": service,
            "status_code": status_code
        })
        super().__init__(message, code="EXTERNAL_SERVICE_ERROR", details=details)


class DatabaseError(SupplyChainError):
    """Raised when database operation fails"""

    def __init__(
        self,
        message: str,
        operation: str = "",
        table: str = "",
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details.update({
            "operation": operation,
            "table": table
        })
        super().__init__(message, code="DATABASE_ERROR", details=details)


# Convenience function to map exceptions to HTTP status codes
def get_http_status_for_exception(exception: SupplyChainError) -> int:
    """Map domain exceptions to appropriate HTTP status codes"""
    status_map = {
        "VALIDATION_ERROR": 400,
        "NOT_FOUND": 404,
        "AUTHENTICATION_ERROR": 401,
        "AUTHORIZATION_ERROR": 403,
        "RATE_LIMIT_EXCEEDED": 429,
        "CAPACITY_EXCEEDED": 400,
        "ROUTE_ERROR": 400,
        "CONFIGURATION_ERROR": 500,
        "OPTIMIZATION_ERROR": 500,
        "QUANTUM_ERROR": 500,
        "EXTERNAL_SERVICE_ERROR": 502,
        "DATABASE_ERROR": 500,
        "UNKNOWN_ERROR": 500
    }
    return status_map.get(exception.code, 500)


# Exception handler decorator for Flask routes
def handle_domain_exceptions(func):
    """Decorator to catch domain exceptions and return appropriate responses"""
    from functools import wraps
    from utils.response import error_response

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SupplyChainError as e:
            status_code = get_http_status_for_exception(e)
            return error_response(
                e.code, e.message, details=e.details, status=status_code
            )
        except Exception as e:
            # Catch any other exceptions and wrap them
            return error_response(
                "INTERNAL_ERROR",
                "An unexpected error occurred",
                details={"original_error": str(e)},
                status=500
            )
    return wrapper
