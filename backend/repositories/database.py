"""
Database repositories for data persistence
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from models.database import (
    Warehouse,
    Customer,
    Route,
    OptimizationJob,
    OptimizationResult,
    Assignment,
    JobStatus,
    OptimizationMethod,
)
from schemas.validation import (
    WarehouseCreate,
    CustomerCreate,
    RouteCreate,
)


class WarehouseRepository:
    """Repository for warehouse operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> List[Warehouse]:
        """Get all warehouses"""
        return self.db.query(Warehouse).all()
    
    def get_by_id(self, warehouse_id: str) -> Optional[Warehouse]:
        """Get warehouse by ID"""
        return (
            self.db.query(Warehouse)
            .filter(Warehouse.id == warehouse_id)
            .first()
        )
    
    def create(self, warehouse_data: WarehouseCreate) -> Warehouse:
        """Create new warehouse"""
        warehouse = Warehouse(**warehouse_data.model_dump())
        self.db.add(warehouse)
        self.db.commit()
        self.db.refresh(warehouse)
        return warehouse
    
    def create_many(
        self, warehouses_data: List[WarehouseCreate]
    ) -> List[Warehouse]:
        """Create multiple warehouses"""
        warehouses = [Warehouse(**w.model_dump()) for w in warehouses_data]
        self.db.add_all(warehouses)
        self.db.commit()
        for warehouse in warehouses:
            self.db.refresh(warehouse)
        return warehouses
    
    def delete_all(self):
        """Delete all warehouses"""
        self.db.query(Warehouse).delete()
        self.db.commit()


class CustomerRepository:
    """Repository for customer operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> List[Customer]:
        """Get all customers"""
        return self.db.query(Customer).all()
    
    def get_by_id(self, customer_id: str) -> Optional[Customer]:
        """Get customer by ID"""
        return (
            self.db.query(Customer)
            .filter(Customer.id == customer_id)
            .first()
        )
    
    def create(self, customer_data: CustomerCreate) -> Customer:
        """Create new customer"""
        customer = Customer(**customer_data.model_dump())
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer
    
    def create_many(
        self, customers_data: List[CustomerCreate]
    ) -> List[Customer]:
        """Create multiple customers"""
        customers = [Customer(**c.model_dump()) for c in customers_data]
        self.db.add_all(customers)
        self.db.commit()
        for customer in customers:
            self.db.refresh(customer)
        return customers
    
    def delete_all(self):
        """Delete all customers"""
        self.db.query(Customer).delete()
        self.db.commit()


class RouteRepository:
    """Repository for route operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> List[Route]:
        """Get all routes"""
        return self.db.query(Route).all()
    
    def get_by_id(self, route_id: str) -> Optional[Route]:
        """Get route by ID"""
        return self.db.query(Route).filter(Route.id == route_id).first()
    
    def create(self, route_data: RouteCreate) -> Route:
        """Create new route"""
        route_dict = route_data.model_dump()
        if not route_dict.get('id'):
            route_dict['id'] = (
                f"{route_dict['warehouse_id']}-{route_dict['customer_id']}"
            )
        
        route = Route(**route_dict)
        self.db.add(route)
        self.db.commit()
        self.db.refresh(route)
        return route
    
    def create_many(self, routes_data: List[RouteCreate]) -> List[Route]:
        """Create multiple routes"""
        routes = []
        for r in routes_data:
            route_dict = r.model_dump()
            if not route_dict.get('id'):
                route_dict['id'] = (
                    f"{route_dict['warehouse_id']}-{route_dict['customer_id']}"
                )
            routes.append(Route(**route_dict))
        
        self.db.add_all(routes)
        self.db.commit()
        for route in routes:
            self.db.refresh(route)
        return routes
    
    def delete_all(self):
        """Delete all routes"""
        self.db.query(Route).delete()
        self.db.commit()


class OptimizationJobRepository:
    """Repository for optimization job operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(
        self,
        method: OptimizationMethod,
        input_data: Dict[str, Any],
        parameters: Optional[Dict[str, Any]] = None,
    ) -> OptimizationJob:
        """Create new optimization job"""
        job = OptimizationJob(
            method=method,
            input_data=input_data,
            parameters=parameters or {}
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job
    
    def get_by_id(self, job_id: str) -> Optional[OptimizationJob]:
        """Get job by ID"""
        return (
            self.db.query(OptimizationJob)
            .filter(OptimizationJob.id == job_id)
            .first()
        )
    
    def update_status(
        self,
        job_id: str,
        status: JobStatus,
        progress: Optional[int] = None,
        error_message: Optional[str] = None,
        error_details: Optional[Dict[str, Any]] = None,
    ):
        """Update job status"""
        job = self.get_by_id(job_id)
        if job:
            job.status = status
            if progress is not None:
                job.progress = progress
            if error_message:
                job.error_message = error_message
            if error_details:
                job.error_details = error_details
            
            if status == JobStatus.RUNNING and not job.started_at:
                job.started_at = datetime.utcnow()
            elif status in [
                JobStatus.COMPLETED,
                JobStatus.FAILED,
                JobStatus.CANCELLED,
            ]:
                job.completed_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(job)
        return job
    
    def get_recent(self, limit: int = 10) -> List[OptimizationJob]:
        """Get recent jobs"""
        return (self.db.query(OptimizationJob)
                .order_by(desc(OptimizationJob.created_at))
                .limit(limit)
                .all())


class OptimizationResultRepository:
    """Repository for optimization result operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(
        self,
        job_id: str,
        result_data: Dict[str, Any],
        total_cost: Optional[float] = None,
        execution_time: Optional[float] = None,
    ) -> OptimizationResult:
        """Create optimization result.

        Accepts mixed key styles in result_data (snake_case or camelCase)
        and optional explicit totals from service layer.
        """
        # Helper to read either casing
        def pick(d: Dict[str, Any], snake: str, camel: str, default=None):
            if snake in d:
                return d.get(snake, default)
            return d.get(camel, default)

        perf = pick(
            result_data,
            'performance_metrics',
            'performanceMetrics',
            {},
        ) or {}

        result = OptimizationResult(
            job_id=job_id,
            total_cost=(
                total_cost
                if total_cost is not None
                else pick(result_data, 'total_cost', 'totalCost', 0)
            ),
            total_co2=pick(result_data, 'total_co2', 'totalCo2', 0),
            avg_delivery_time=pick(
                result_data, 'avg_delivery_time', 'avgDeliveryTime', 0
            ),
            routes_used=pick(result_data, 'routes_used', 'routesUsed', 0),
            optimization_time=(
                execution_time
                if execution_time is not None
                else pick(
                    perf,
                    'optimization_time_seconds',
                    'optimizationTimeSeconds',
                    0,
                )
            ),
            iterations=pick(perf, 'iterations', 'iterations', 0),
            convergence=pick(perf, 'convergence', 'convergence', False),
            routes_data=pick(result_data, 'routes', 'routes', []),
            assignments_data=pick(
                result_data, 'assignments', 'assignments', []
            ),
            performance_metrics=perf,
        )
        
        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)
        
        # Create assignments
        assignments = []
        for assignment_data in result_data.get('assignments', []):
            assignment = Assignment(
                result_id=result.id,
                warehouse_id=assignment_data.get('warehouseId'),
                customer_id=assignment_data.get('customerId'),
                demand=assignment_data.get('demand', 0),
                cost=assignment_data.get('cost', 0),
                co2=assignment_data.get('co2', 0),
                distance_km=assignment_data.get('distanceKm', 0),
                delivery_time_hours=assignment_data.get('deliveryTimeHours', 0)
            )
            assignments.append(assignment)
        
        if assignments:
            self.db.add_all(assignments)
            self.db.commit()
        
        return result
    
    def get_by_id(self, result_id: str) -> Optional[OptimizationResult]:
        """Get result by ID"""
        return (
            self.db.query(OptimizationResult)
            .filter(OptimizationResult.id == result_id)
            .first()
        )
    
    def get_by_job_id(self, job_id: str) -> Optional[OptimizationResult]:
        """Get result by job ID"""
        return (
            self.db.query(OptimizationResult)
            .filter(OptimizationResult.job_id == job_id)
            .first()
        )
    
    def get_recent(self, limit: int = 10) -> List[OptimizationResult]:
        """Get recent results"""
        return (self.db.query(OptimizationResult)
                .order_by(desc(OptimizationResult.created_at))
                .limit(limit)
                .all())
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        total_results = (
            self.db.query(func.count(OptimizationResult.id)).scalar()
        )
        recent_count = (
            self.db.query(func.count(OptimizationResult.id))
            .filter(
                OptimizationResult.created_at
                >= datetime.utcnow().replace(hour=0, minute=0, second=0)
            )
            .scalar()
        )
        
        avg_cost = self.db.query(
            func.avg(OptimizationResult.total_cost)
        ).scalar() or 0
        avg_co2 = self.db.query(
            func.avg(OptimizationResult.total_co2)
        ).scalar() or 0
        
        return {
            'total_results': total_results,
            'recent_count': recent_count,
            'avg_cost': float(avg_cost),
            'avg_co2': float(avg_co2)
        }
