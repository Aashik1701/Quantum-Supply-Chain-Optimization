"""
Pydantic schemas for request/response validation
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator, ConfigDict
from pydantic.types import confloat, conint, constr


class OptimizationMethodEnum(str, Enum):
    CLASSICAL = "classical"
    QUANTUM = "quantum"
    HYBRID = "hybrid"


class JobStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# Base schemas
class WarehouseBase(BaseModel):
    id: constr(min_length=1, max_length=50) = Field(..., description="Unique warehouse identifier")
    name: constr(min_length=1, max_length=255) = Field(..., description="Warehouse name")
    country: constr(min_length=1, max_length=100) = Field(..., description="Country")
    latitude: confloat(ge=-90, le=90) = Field(..., description="Latitude coordinate")
    longitude: confloat(ge=-180, le=180) = Field(..., description="Longitude coordinate")
    capacity: conint(gt=0) = Field(..., description="Warehouse capacity")
    operating_cost: confloat(ge=0) = Field(0.0, description="Operating cost per unit")


class CustomerBase(BaseModel):
    id: constr(min_length=1, max_length=50) = Field(..., description="Unique customer identifier")
    name: constr(min_length=1, max_length=255) = Field(..., description="Customer name")
    country: constr(min_length=1, max_length=100) = Field(..., description="Country")
    latitude: confloat(ge=-90, le=90) = Field(..., description="Latitude coordinate")
    longitude: confloat(ge=-180, le=180) = Field(..., description="Longitude coordinate")
    demand: conint(gt=0) = Field(..., description="Customer demand")
    priority: PriorityEnum = Field(PriorityEnum.MEDIUM, description="Customer priority")


class RouteBase(BaseModel):
    id: Optional[str] = Field(None, description="Route identifier")
    warehouse_id: constr(min_length=1, max_length=50) = Field(..., description="Warehouse ID")
    customer_id: constr(min_length=1, max_length=50) = Field(..., description="Customer ID")
    distance_km: confloat(gt=0) = Field(..., description="Distance in kilometers")
    transport_mode: str = Field("truck", description="Transport mode")
    cost_per_km: confloat(ge=0) = Field(1.0, description="Cost per kilometer")
    co2_per_km: confloat(ge=0) = Field(0.4, description="CO2 emissions per kilometer")
    speed_kmh: confloat(gt=0) = Field(80.0, description="Speed in km/h")


# Request schemas
class WarehouseCreate(WarehouseBase):
    pass


class CustomerCreate(CustomerBase):
    pass


class RouteCreate(RouteBase):
    pass


class OptimizationRequest(BaseModel):
    method: OptimizationMethodEnum = Field(..., description="Optimization method")
    warehouses: List[WarehouseBase] = Field(..., min_items=1, description="List of warehouses")
    customers: List[CustomerBase] = Field(..., min_items=1, description="List of customers")
    routes: Optional[List[RouteBase]] = Field(None, description="Optional predefined routes")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Method-specific parameters")
    
    @validator('warehouses')
    def validate_unique_warehouse_ids(cls, v):
        ids = [w.id for w in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Warehouse IDs must be unique")
        return v
    
    @validator('customers')
    def validate_unique_customer_ids(cls, v):
        ids = [c.id for c in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Customer IDs must be unique")
        return v


class DataValidationRequest(BaseModel):
    warehouses: Optional[List[WarehouseBase]] = Field(None, description="Warehouses to validate")
    customers: Optional[List[CustomerBase]] = Field(None, description="Customers to validate")
    routes: Optional[List[RouteBase]] = Field(None, description="Routes to validate")


# Response schemas
class WarehouseResponse(WarehouseBase):
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CustomerResponse(CustomerBase):
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class RouteResponse(RouteBase):
    id: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AssignmentResponse(BaseModel):
    customer_id: str = Field(..., description="Customer ID")
    warehouse_id: str = Field(..., description="Warehouse ID")
    demand: int = Field(..., description="Demand fulfilled")
    cost: float = Field(..., description="Assignment cost")
    co2: float = Field(..., description="CO2 emissions")
    distance_km: float = Field(..., description="Distance in kilometers")
    delivery_time_hours: float = Field(..., description="Delivery time in hours")
    
    model_config = ConfigDict(from_attributes=True)


class OptimizationRouteResponse(BaseModel):
    id: str = Field(..., description="Route ID")
    warehouse_id: str = Field(..., description="Warehouse ID")
    customer_id: str = Field(..., description="Customer ID")
    distance_km: float = Field(..., description="Distance in kilometers")
    total_cost: float = Field(..., description="Total route cost")
    total_co2: float = Field(..., description="Total CO2 emissions")
    delivery_time_hours: float = Field(..., description="Delivery time in hours")
    
    model_config = ConfigDict(from_attributes=True)


class PerformanceMetrics(BaseModel):
    optimization_time_seconds: float = Field(..., description="Optimization time")
    iterations: int = Field(..., description="Number of iterations")
    convergence: bool = Field(..., description="Whether optimization converged")


class OptimizationResultResponse(BaseModel):
    id: str = Field(..., description="Result ID")
    method: OptimizationMethodEnum = Field(..., description="Optimization method")
    total_cost: float = Field(..., description="Total cost")
    total_co2: float = Field(..., description="Total CO2 emissions")
    avg_delivery_time: float = Field(..., description="Average delivery time")
    routes_used: int = Field(..., description="Number of routes used")
    routes: List[OptimizationRouteResponse] = Field(..., description="Optimized routes")
    assignments: List[AssignmentResponse] = Field(..., description="Customer assignments")
    performance_metrics: PerformanceMetrics = Field(..., description="Performance metrics")
    created_at: datetime = Field(..., description="Result creation time")
    
    model_config = ConfigDict(from_attributes=True)


class JobResponse(BaseModel):
    id: str = Field(..., description="Job ID")
    method: OptimizationMethodEnum = Field(..., description="Optimization method")
    status: JobStatusEnum = Field(..., description="Job status")
    progress: int = Field(..., description="Progress percentage")
    created_at: datetime = Field(..., description="Job creation time")
    started_at: Optional[datetime] = Field(None, description="Job start time")
    completed_at: Optional[datetime] = Field(None, description="Job completion time")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    model_config = ConfigDict(from_attributes=True)


class OptimizationResponse(BaseModel):
    job: JobResponse = Field(..., description="Job information")
    result: Optional[OptimizationResultResponse] = Field(None, description="Result if completed")
    
    model_config = ConfigDict(from_attributes=True)


class ValidationError(BaseModel):
    field: str = Field(..., description="Field with error")
    message: str = Field(..., description="Error message")
    value: Any = Field(..., description="Invalid value")


class ValidationResponse(BaseModel):
    valid: bool = Field(..., description="Whether data is valid")
    errors: List[Any] = Field(default_factory=list, description="List of validation errors")
    warnings: List[str] = Field(default_factory=list, description="List of warnings")
    summary: Dict[str, int] = Field(..., description="Summary statistics")
    
    model_config = ConfigDict(from_attributes=True)


class DashboardSummary(BaseModel):
    total_warehouses: int = Field(..., description="Total number of warehouses")
    total_customers: int = Field(..., description="Total number of customers")
    total_routes: int = Field(..., description="Total number of routes")
    recent_optimizations: int = Field(..., description="Recent optimizations count")
    
    model_config = ConfigDict(from_attributes=True)


class DashboardResponse(BaseModel):
    summary: DashboardSummary = Field(..., description="Dashboard summary")
    recent_results: List[OptimizationResultResponse] = Field(..., description="Recent results")
    
    model_config = ConfigDict(from_attributes=True)


# Error response schemas
class ErrorDetail(BaseModel):
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class ErrorResponse(BaseModel):
    success: bool = Field(False, description="Success status")
    error: ErrorDetail = Field(..., description="Error information")
    meta: Dict[str, Any] = Field(..., description="Request metadata")
    
    model_config = ConfigDict(from_attributes=True)
