"""
Database-enabled data service replacing in-memory storage
"""

import csv
import io
from typing import List, Dict, Any
from contextlib import contextmanager

from config.database import get_db
from repositories.database import (
    WarehouseRepository, CustomerRepository, RouteRepository
)
from schemas.validation import (
    WarehouseCreate, CustomerCreate, RouteCreate,
    ValidationResponse, ValidationError
)
from utils.exceptions import ValidationError as DomainValidationError


class DatabaseDataService:
    """Database-enabled data service"""
    
    @contextmanager
    def _get_db_session(self):
        """Get database session with context management"""
        db = next(get_db())
        try:
            yield db
        finally:
            db.close()
    
    def get_warehouses(self) -> List[Dict[str, Any]]:
        """Get all warehouses"""
        with self._get_db_session() as db:
            repo = WarehouseRepository(db)
            warehouses = repo.get_all()
            return [
                {
                    'id': w.id,
                    'name': w.name,
                    'country': w.country,
                    'latitude': w.latitude,
                    'longitude': w.longitude,
                    'capacity': w.capacity,
                    'operatingCost': w.operating_cost
                }
                for w in warehouses
            ]

    def create_warehouse(
        self, warehouse_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a single warehouse"""
        try:
            # Validate data
            validated_warehouse = WarehouseCreate(**warehouse_data)
            
            with self._get_db_session() as db:
                repo = WarehouseRepository(db)
                warehouse = repo.create(validated_warehouse)
                
                return {
                    'id': warehouse.id,
                    'name': warehouse.name,
                    'country': warehouse.country,
                    'latitude': warehouse.latitude,
                    'longitude': warehouse.longitude,
                    'capacity': warehouse.capacity,
                    'operatingCost': warehouse.operating_cost
                }
        except Exception as e:
            raise DomainValidationError(
                f'Failed to create warehouse: {str(e)}'
            )

    def get_customers(self) -> List[Dict[str, Any]]:
        """Get all customers"""
        with self._get_db_session() as db:
            repo = CustomerRepository(db)
            customers = repo.get_all()
            return [
                {
                    'id': c.id,
                    'name': c.name,
                    'country': c.country,
                    'latitude': c.latitude,
                    'longitude': c.longitude,
                    'demand': c.demand,
                    'priority': c.priority
                }
                for c in customers
            ]

    def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a single customer"""
        try:
            # Validate data
            validated_customer = CustomerCreate(**customer_data)
            
            with self._get_db_session() as db:
                repo = CustomerRepository(db)
                customer = repo.create(validated_customer)
                
                return {
                    'id': customer.id,
                    'name': customer.name,
                    'country': customer.country,
                    'latitude': customer.latitude,
                    'longitude': customer.longitude,
                    'demand': customer.demand,
                    'priority': customer.priority
                }
        except Exception as e:
            raise DomainValidationError(f'Failed to create customer: {str(e)}')

    def get_routes(self) -> List[Dict[str, Any]]:
        """Get all routes"""
        with self._get_db_session() as db:
            repo = RouteRepository(db)
            routes = repo.get_all()
            result: List[Dict[str, Any]] = []
            for r in routes:
                # Compute cost & duration from available fields
                distance_km = (
                    float(r.distance_km) if r.distance_km is not None else 0.0
                )
                cost_per_km = (
                    float(r.cost_per_km) if r.cost_per_km is not None else 0.0
                )
                speed_kmh = (
                    float(r.speed_kmh)
                    if r.speed_kmh is not None and r.speed_kmh != 0
                    else 80.0
                )

                cost = distance_km * cost_per_km
                duration = distance_km / speed_kmh if speed_kmh > 0 else 0.0

                result.append({
                    'id': r.id,
                    'warehouseId': r.warehouse_id,
                    'customerId': r.customer_id,
                    'distanceKm': distance_km,
                    'transportMode': r.transport_mode,
                    'cost': cost,
                    'duration': duration,
                    # Expose additional fields for richer UIs
                    'costPerKm': cost_per_km,
                    'co2PerKm': (
                        float(r.co2_per_km)
                        if r.co2_per_km is not None
                        else 0.0
                    ),
                    'speedKmh': speed_kmh,
                })
            return result

    def create_route(self, route_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a single route"""
        try:
            # Validate data
            validated_route = RouteCreate(**route_data)
            
            with self._get_db_session() as db:
                repo = RouteRepository(db)
                route = repo.create(validated_route)
                
                return {
                    'id': route.id,
                    'warehouseId': route.warehouse_id,
                    'customerId': route.customer_id,
                    'distanceKm': route.distance_km,
                    'transportMode': route.transport_mode,
                    'cost': route.cost,
                    'duration': route.duration
                }
        except Exception as e:
            raise DomainValidationError(f'Failed to create route: {str(e)}')

    def validate_data(self, data: Dict[str, Any]) -> ValidationResponse:
        """Validate supply chain data"""
        errors = []
        warnings = []
        
        # Validate warehouses
        warehouses = data.get('warehouses', [])
        for i, warehouse in enumerate(warehouses):
            try:
                WarehouseCreate(**warehouse)
            except Exception as e:
                errors.append(ValidationError(
                    field=f"warehouses[{i}]",
                    message=str(e),
                    value=warehouse
                ))
        
        # Validate customers
        customers = data.get('customers', [])
        for i, customer in enumerate(customers):
            try:
                CustomerCreate(**customer)
            except Exception as e:
                errors.append(ValidationError(
                    field=f"customers[{i}]",
                    message=str(e),
                    value=customer
                ))
        
        # Validate routes
        routes = data.get('routes', [])
        for i, route in enumerate(routes):
            try:
                RouteCreate(**route)
            except Exception as e:
                errors.append(ValidationError(
                    field=f"routes[{i}]",
                    message=str(e),
                    value=route
                ))
        
        # Business logic validation
        if warehouses and customers:
            total_capacity = sum(w.get('capacity', 0) for w in warehouses)
            total_demand = sum(c.get('demand', 0) for c in customers)
            
            if total_capacity < total_demand:
                warnings.append(
                    f"Total capacity ({total_capacity}) is less than "
                    f"total demand ({total_demand})"
                )
        
        # Convert ValidationError objects to dicts for JSON serialization
        error_dicts = []
        for err in errors:
            if hasattr(err, 'model_dump'):
                error_dicts.append(err.model_dump())
            elif hasattr(err, 'dict'):
                error_dicts.append(err.dict())
            elif isinstance(err, dict):
                error_dicts.append(err)
            else:
                error_dicts.append({'message': str(err)})
        
        return ValidationResponse(
            valid=len(errors) == 0,
            errors=error_dicts,
            warnings=warnings,
            summary={
                'warehouses': len(warehouses),
                'customers': len(customers),
                'routes': len(routes)
            }
        )

    def upload_warehouses(
        self, warehouses_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Upload multiple warehouses"""
        try:
            # Validate all warehouses first
            validated_warehouses = [
                WarehouseCreate(**w) for w in warehouses_data
            ]
            
            with self._get_db_session() as db:
                repo = WarehouseRepository(db)
                count = 0
                for warehouse_data in validated_warehouses:
                    repo.create(warehouse_data)
                    count += 1
                
                return {
                    'success': True,
                    'count': count,
                    'message': (
                        f'Successfully uploaded {count} warehouses'
                    )
                }
        except Exception as e:
            raise DomainValidationError(
                f'Failed to upload warehouses: {str(e)}'
            )

    def upload_customers(
        self, customers_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Upload multiple customers"""
        try:
            # Validate all customers first
            validated_customers = [CustomerCreate(**c) for c in customers_data]
            
            with self._get_db_session() as db:
                repo = CustomerRepository(db)
                count = 0
                for customer_data in validated_customers:
                    repo.create(customer_data)
                    count += 1
                
                return {
                    'success': True,
                    'count': count,
                    'message': (
                        f'Successfully uploaded {count} customers'
                    )
                }
        except Exception as e:
            raise DomainValidationError(
                f'Failed to upload customers: {str(e)}'
            )

    def upload_routes(
        self, routes_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Upload multiple routes"""
        try:
            # Validate all routes first
            validated_routes = [RouteCreate(**r) for r in routes_data]
            
            with self._get_db_session() as db:
                repo = RouteRepository(db)
                count = 0
                for route_data in validated_routes:
                    repo.create(route_data)
                    count += 1
                
                return {
                    'success': True,
                    'count': count,
                    'message': f'Successfully uploaded {count} routes'
                }
        except Exception as e:
            raise DomainValidationError(f'Failed to upload routes: {str(e)}')

    def process_csv_upload(
        self, file_content: str, data_type: str
    ) -> Dict[str, Any]:
        """Process CSV file upload"""
        try:
            reader = csv.DictReader(io.StringIO(file_content))
            raw_rows = list(reader)

            if data_type == 'warehouses':
                # Normalize warehouses headers/fields
                norm_wh: List[Dict[str, Any]] = []
                for r in raw_rows:
                    try:
                        oc = (
                            r.get('operating_cost')
                            or r.get('operating_cost_per_unit')
                            or r.get('operatingCostPerUnit')
                            or r.get('operatingCost')
                            or 0
                        )
                        norm_wh.append({
                            'id': (
                                r.get('id')
                                or r.get('warehouse_id')
                                or r.get('warehouseId')
                            ),
                            'name': (
                                r.get('name')
                                or r.get('warehouse_name')
                                or r.get('warehouseName')
                            ),
                            'country': r.get('country'),
                            'latitude': float(
                                (r.get('latitude') or '').strip() or 0
                            ),
                            'longitude': float(
                                (r.get('longitude') or '').strip() or 0
                            ),
                            'capacity': int(
                                float((r.get('capacity') or '').strip() or 0)
                            ),
                            'operating_cost': float(str(oc).strip() or 0),
                        })
                    except Exception:
                        norm_wh.append(r)
                return self.upload_warehouses(norm_wh)

            if data_type == 'customers':
                # Normalize customers (priority mapping)
                norm_cu: List[Dict[str, Any]] = []
                for r in raw_rows:
                    pri = r.get('priority')
                    pri_s = (
                        str(pri).strip().lower() if pri is not None else ''
                    )
                    if pri_s in {'1', 'high', 'h'}:
                        pri_norm = 'high'
                    elif pri_s in {'2', 'medium', 'med', 'm'}:
                        pri_norm = 'medium'
                    elif pri_s in {'3', 'low', 'l'}:
                        pri_norm = 'low'
                    else:
                        pri_norm = 'medium'
                    try:
                        norm_cu.append({
                            'id': (
                                r.get('id')
                                or r.get('customer_id')
                                or r.get('customerId')
                            ),
                            'name': (
                                r.get('name')
                                or r.get('customer_name')
                                or r.get('customerName')
                            ),
                            'country': r.get('country'),
                            'latitude': float(
                                (r.get('latitude') or '').strip() or 0
                            ),
                            'longitude': float(
                                (r.get('longitude') or '').strip() or 0
                            ),
                            'demand': int(
                                float((r.get('demand') or '').strip() or 0)
                            ),
                            'priority': pri_norm,
                        })
                    except Exception:
                        norm_cu.append(r)
                return self.upload_customers(norm_cu)

            if data_type == 'routes':
                # Normalize routes headers/fields
                norm_rt: List[Dict[str, Any]] = []
                for r in raw_rows:
                    if (
                        'warehouse_id' in r
                        and 'customer_id' in r
                        and 'distance_km' in r
                    ):
                        val = r.get('speed_kmh')
                        item = {
                            'id': r.get('id'),
                            'warehouse_id': r.get('warehouse_id'),
                            'customer_id': r.get('customer_id'),
                            'distance_km': float(r.get('distance_km') or 0),
                            'transport_mode': (
                                r.get('transport_mode', 'truck')
                            ),
                            'cost_per_km': float(
                                r.get('cost_per_km')
                                or r.get('cost_per_unit')
                                or 0
                            ),
                            'co2_per_km': float(
                                r.get('co2_per_km')
                                or r.get('co2_per_unit')
                                or 0
                            ),
                            'speed_kmh': (
                                float(str(val))
                                if val not in (None, '')
                                else (
                                    float(r.get('distance_km') or 0)
                                    / (
                                        float(
                                            r.get(
                                                'delivery_time_days'
                                            )
                                            or 0
                                        )
                                        * 24
                                        if float(
                                            r.get(
                                                'delivery_time_days'
                                            )
                                            or 0
                                        )
                                        > 0
                                        else 80.0
                                    )
                                )
                            ),
                        }
                        if (
                            not item['id']
                            and item['warehouse_id']
                            and item['customer_id']
                        ):
                            mode = str(item['transport_mode']).lower()
                            item['id'] = (
                                f"{item['warehouse_id']}"
                                f"-{item['customer_id']}"
                                f"-{mode}"
                            )
                        norm_rt.append(item)
                    else:
                        norm_rt.append(r)
                return self.upload_routes(norm_rt)

            # Unknown data type
            raise DomainValidationError(
                f'Invalid data type: {data_type}'
            )

        except Exception as e:
            if isinstance(e, DomainValidationError):
                raise
            raise DomainValidationError(
                f'Failed to process CSV: {str(e)}'
            )

    def process_upload(self, file, data_type: str) -> Dict[str, Any]:
        """Process uploaded file with validation"""
        try:
            # Validate file presence
            if not file or not file.filename:
                raise DomainValidationError('No file provided')
            
            # Validate file extension
            filename = file.filename.lower()
            if not filename.endswith('.csv'):
                raise DomainValidationError('Only CSV files are supported')
            
            # Validate data type
            valid_types = ['warehouses', 'customers', 'routes']
            if data_type not in valid_types:
                raise DomainValidationError(
                    f'Invalid data type. Must be one of: {valid_types}'
                )
            
            # Read file content
            try:
                file_content = file.read().decode('utf-8')
                # Reset file pointer in case it's needed elsewhere
                file.seek(0)
            except UnicodeDecodeError:
                raise DomainValidationError('File must be UTF-8 encoded')
            
            # Validate file size (limit to 10MB)
            if len(file_content.encode('utf-8')) > 10 * 1024 * 1024:
                raise DomainValidationError('File size must be less than 10MB')
            
            # Validate content is not empty
            if not file_content.strip():
                raise DomainValidationError('File content is empty')
            
            # Delegate to CSV processing
            return self.process_csv_upload(file_content, data_type)
            
        except Exception as e:
            if isinstance(e, DomainValidationError):
                raise
            raise DomainValidationError(f'Failed to process upload: {str(e)}')

    def get_summary(self) -> Dict[str, Any]:
        """Get database summary statistics"""
        with self._get_db_session() as db:
            warehouse_repo = WarehouseRepository(db)
            customer_repo = CustomerRepository(db)
            route_repo = RouteRepository(db)
            
            warehouses = warehouse_repo.get_all()
            customers = customer_repo.get_all()
            routes = route_repo.get_all()
            
            return {
                'warehouses': len(warehouses),
                'customers': len(customers),
                'routes': len(routes),
                'total_capacity': sum(w.capacity for w in warehouses),
                'total_demand': sum(c.demand for c in customers)
            }

    def get_sample_data(self) -> Dict[str, Any]:
        """Get sample data for testing"""
        return {
            'warehouses': [
                {
                    'id': 'W001',
                    'name': 'Central Warehouse',
                    'country': 'USA',
                    'latitude': 40.7128,
                    'longitude': -74.0060,
                    'capacity': 1000,
                    'operating_cost': 100.0
                }
            ],
            'customers': [
                {
                    'id': 'C001',
                    'name': 'Customer A',
                    'country': 'USA',
                    'latitude': 40.7589,
                    'longitude': -73.9851,
                    'demand': 100,
                    'priority': 1
                }
            ],
            'routes': [
                {
                    'warehouse_id': 'W001',
                    'customer_id': 'C001',
                    'distance_km': 5.0,
                    'transport_mode': 'TRUCK',
                    'cost': 10.0,
                    'duration': 1.0
                }
            ]
        }

    def delete_data(self, data_type: str) -> Dict[str, Any]:
        """Delete all data of a specific type"""
        try:
            with self._get_db_session() as db:
                if data_type == 'warehouses':
                    w_repo = WarehouseRepository(db)
                    w_repo.delete_all()
                    return {
                        'success': True,
                        'message': 'All warehouses deleted successfully'
                    }
                elif data_type == 'customers':
                    c_repo = CustomerRepository(db)
                    c_repo.delete_all()
                    return {
                        'success': True,
                        'message': 'All customers deleted successfully'
                    }
                elif data_type == 'routes':
                    r_repo = RouteRepository(db)
                    r_repo.delete_all()
                    return {
                        'success': True,
                        'message': 'All routes deleted successfully'
                    }
                else:
                    raise DomainValidationError(
                        f'Invalid data type: {data_type}'
                    )
        except Exception as e:
            if isinstance(e, DomainValidationError):
                raise
            raise DomainValidationError(
                f'Failed to delete {data_type}: {str(e)}'
            )
