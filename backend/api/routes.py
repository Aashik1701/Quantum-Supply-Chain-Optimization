"""
Main API routes for Hybrid Quantum-Classical Supply Chain Optimization
"""

from flask import Blueprint, request
from utils.response import success_response, error_response
from utils.exceptions import (
    ValidationError, 
    OptimizationError, 
    DataNotFoundError,
    handle_domain_exceptions
)
from services.optimization_service import OptimizationService
from services.database_data_service import DatabaseDataService
from utils.validators import validate_optimization_request

api_bp = Blueprint('api', __name__)

# Services - using simple in-memory service for testing
optimization_service = OptimizationService()
data_service = DatabaseDataService()


def init_routes(socketio):
    """Initialize routes with socketio instance"""
    # Using simple optimization service - no socketio needed for now
    pass


@api_bp.route('/health', methods=['GET'])
def health():
    """API health check"""
    return success_response({'status': 'healthy', 'service': 'api'})


@api_bp.route('/backends', methods=['GET'])
@handle_domain_exceptions
def list_backends():
    """List available quantum backends"""
    from config.quantum_config import ibm_quantum
    
    try:
        backends_info = ibm_quantum.get_backends_info()
        return success_response({
            'backends': backends_info,
            'connected': ibm_quantum.service is not None
        }, message='Backends retrieved successfully')
    except Exception as e:
        return success_response({
            'backends': [],
            'connected': False,
            'error': str(e)
        }, message='Could not retrieve backends')


# Optimization endpoints
@api_bp.route('/optimize', methods=['POST'])
@handle_domain_exceptions
def optimize():
    """Generic optimization dispatcher endpoint"""
    payload = request.get_json(silent=True)
    if not payload:
        raise ValidationError('No data provided')
    
    method = payload.get('method', 'hybrid').lower()
    
    # Extract data - frontend sends it nested under 'data' key
    # Backend expects warehouses, customers, routes at root level
    data = payload.get('data', {})
    
    # Merge parameters and data for optimization
    optimization_data = {
        'method': method,
        'warehouses': data.get('warehouses', []),
        'customers': data.get('customers', []),
        'routes': data.get('routes', []),
        'parameters': payload.get('parameters', {}),
        'backendPolicy': payload.get('backendPolicy', 'simulator'),
        'backendName': payload.get('backendName'),
        'jobMode': payload.get('jobMode', 'inline')
    }
    
    # Route to specific optimization method
    if method == 'classical':
        return _run_classical_optimization(optimization_data)
    elif method == 'quantum':
        return _run_quantum_optimization(optimization_data)
    elif method == 'hybrid':
        return _run_hybrid_optimization(optimization_data)
    else:
        raise ValidationError(
            f'Invalid method: {method}. Expected classical/quantum/hybrid'
        )


def _run_classical_optimization(data):
    """Internal classical optimization logic"""
    # Provide detailed validation error message
    if 'warehouses' not in data:
        raise ValidationError('Missing required field: warehouses')
    if 'customers' not in data:
        raise ValidationError('Missing required field: customers')
    if not isinstance(data.get('warehouses'), list) or len(data.get('warehouses', [])) == 0:
        raise ValidationError('warehouses must be a non-empty array')
    if not isinstance(data.get('customers'), list) or len(data.get('customers', [])) == 0:
        raise ValidationError('customers must be a non-empty array')
    
    if not validate_optimization_request(data):
        raise ValidationError('Invalid input data for classical optimization. Check that warehouses and customers have required fields: id, name, latitude, longitude, capacity/demand')
    
    try:
        result = optimization_service.run_classical_optimization(data)
        return success_response(
            {'method': 'classical', 'result': result},
            message='Optimization completed'
        )
    except Exception as e:
        raise OptimizationError(
            'Classical optimization failed', 
            method='classical', 
            details={'error': str(e)}
        )


def _run_quantum_optimization(data):
    """Internal quantum optimization logic"""
    # Provide detailed validation error message
    if 'warehouses' not in data:
        raise ValidationError('Missing required field: warehouses')
    if 'customers' not in data:
        raise ValidationError('Missing required field: customers')
    if not isinstance(data.get('warehouses'), list) or len(data.get('warehouses', [])) == 0:
        raise ValidationError('warehouses must be a non-empty array')
    if not isinstance(data.get('customers'), list) or len(data.get('customers', [])) == 0:
        raise ValidationError('customers must be a non-empty array')
    
    if not validate_optimization_request(data):
        raise ValidationError('Invalid input data for quantum optimization. Check that warehouses and customers have required fields: id, name, latitude, longitude, capacity/demand')
    
    # Extract backend selection parameters
    backend_policy = data.get('backendPolicy', 'simulator')  # 'simulator', 'device', 'shortest_queue'
    backend_name = data.get('backendName')  # Optional specific backend
    job_mode = data.get('jobMode', 'inline')  # 'inline' or 'batch'
    
    try:
        if job_mode == 'batch':
            enqueue_info = optimization_service.enqueue_quantum_job(
                data,
                backend_policy=backend_policy,
                backend_name=backend_name,
            )
            return success_response(
                {
                    'method': 'quantum',
                    'jobMode': 'batch',
                    'job': enqueue_info,
                },
                message='Quantum job enqueued'
            )
        else:
            result = optimization_service.run_quantum_optimization(
                data, 
                backend_policy=backend_policy,
                backend_name=backend_name
            )
            return success_response(
                {'method': 'quantum', 'result': result},
                message='Optimization completed'
            )
    except Exception as e:
        raise OptimizationError(
            'Quantum optimization failed', 
            method='quantum', 
            details={'error': str(e)}
        )


def _run_hybrid_optimization(data):
    """Internal hybrid optimization logic"""
    # Provide detailed validation error message
    if 'warehouses' not in data:
        raise ValidationError('Missing required field: warehouses')
    if 'customers' not in data:
        raise ValidationError('Missing required field: customers')
    if not isinstance(data.get('warehouses'), list) or len(data.get('warehouses', [])) == 0:
        raise ValidationError('warehouses must be a non-empty array')
    if not isinstance(data.get('customers'), list) or len(data.get('customers', [])) == 0:
        raise ValidationError('customers must be a non-empty array')
    
    if not validate_optimization_request(data):
        raise ValidationError('Invalid input data for hybrid optimization. Check that warehouses and customers have required fields: id, name, latitude, longitude, capacity/demand')
    
    try:
        result = optimization_service.run_hybrid_optimization(data)
        return success_response(
            {'method': 'hybrid', 'result': result},
            message='Optimization completed'
        )
    except Exception as e:
        raise OptimizationError(
            'Hybrid optimization failed', 
            method='hybrid', 
            details={'error': str(e)}
        )


@api_bp.route('/optimize/classical', methods=['POST'])
def optimize_classical():
    """Run classical optimization"""
    try:
        data = request.get_json()
        return _run_classical_optimization(data)
    except Exception as e:  # pragma: no cover
        return error_response(
            'OPTIMIZATION_FAILED', 'Optimization failed',
            details=str(e), status=500
        )


@api_bp.route('/optimize/quantum', methods=['POST'])
def optimize_quantum():
    """Run quantum optimization (QAOA)"""
    try:
        data = request.get_json()
        return _run_quantum_optimization(data)
    except Exception as e:  # pragma: no cover
        return error_response(
            'OPTIMIZATION_FAILED', 'Quantum optimization failed',
            details=str(e), status=500
        )


@api_bp.route('/optimize/hybrid', methods=['POST'])
def optimize_hybrid():
    """Run hybrid quantum-classical optimization"""
    try:
        data = request.get_json()
        return _run_hybrid_optimization(data)
    except Exception as e:  # pragma: no cover
        return error_response(
            'OPTIMIZATION_FAILED', 'Hybrid optimization failed',
            details=str(e), status=500
        )


@api_bp.route('/optimize/multi-objective', methods=['POST'])
@handle_domain_exceptions
def optimize_multi_objective():
    """
    Run multi-objective optimization with weight sweep.
    
    Expects:
    - method: 'classical', 'quantum', or 'hybrid'
    - weightConfigs: List of weight configurations [{cost, co2, time}, ...]
    - data: Standard optimization input data
    
    Returns Pareto front and all solutions with dominance info.
    """
    from utils.pareto import compute_pareto_front, compute_quality_metrics
    
    request_data = request.get_json(silent=True)
    if not request_data:
        raise ValidationError('No data provided')
    
    method = request_data.get('method', 'hybrid').lower()
    weight_configs = request_data.get('weightConfigs', [])
    optimization_data = request_data.get('data', {})
    
    if not weight_configs:
        raise ValidationError('No weight configurations provided')
    
    if not validate_optimization_request(optimization_data):
        raise ValidationError('Invalid optimization data')
    
    # Run optimization for each weight configuration
    solutions = []
    
    for idx, weights in enumerate(weight_configs):
        # Add weights to optimization data
        opt_data = {**optimization_data, 'weights': weights}
        
        try:
            # Route to appropriate optimization method
            if method == 'classical':
                result = optimization_service.run_classical_optimization(opt_data)
            elif method == 'quantum':
                result = optimization_service.run_quantum_optimization(
                    opt_data,
                    backend_policy=request_data.get('backendPolicy', 'simulator'),
                    backend_name=request_data.get('backendName')
                )
            elif method == 'hybrid':
                result = optimization_service.run_hybrid_optimization(opt_data)
            else:
                continue
            
            # Extract objectives from result
            solution = {
                'id': f"{method}_{idx}",
                'method': method,
                'weights': weights,
                'cost': result.get('totalCost', 0),
                'co2': result.get('totalCO2', 0),
                'time': result.get('totalTime', 0),
                'routes': result.get('routes', []),
                'metadata': {
                    'solveTime': result.get('solveTime', 0),
                    'backend': result.get('backend'),
                }
            }
            solutions.append(solution)
            
        except Exception as e:
            # Log error but continue with other configurations
            print(f"Warning: Optimization failed for weights {weights}: {str(e)}")
            continue
    
    if not solutions:
        raise OptimizationError(
            'All optimizations failed',
            method='multi-objective',
            details={'count': len(weight_configs)}
        )
    
    # Compute Pareto front
    pareto_front, dominated = compute_pareto_front(solutions)
    
    # Compute quality metrics
    # Use worst values as reference point
    reference_point = {
        'cost': max(s['cost'] for s in solutions) * 1.1,
        'co2': max(s['co2'] for s in solutions) * 1.1,
        'time': max(s['time'] for s in solutions) * 1.1,
    }
    quality_metrics = compute_quality_metrics(pareto_front, reference_point)
    
    return success_response({
        'method': 'multi-objective',
        'solutions': solutions,
        'paretoFront': pareto_front,
        'dominated': dominated,
        'metrics': quality_metrics,
        'weightConfigs': weight_configs,
    }, message=f'Multi-objective optimization completed: {len(pareto_front)} Pareto optimal solutions')


@api_bp.route('/optimize/vrp', methods=['POST'])
@handle_domain_exceptions
def optimize_vrp():
    """Run Vehicle Routing Problem (VRP) optimization"""
    data = request.get_json(silent=True)
    if not data:
        raise ValidationError('No data provided')
    
    try:
        result = optimization_service.run_vrp_optimization(data)
        return success_response(
            {'method': 'vrp', 'result': result},
            message='VRP optimization completed'
        )
    except Exception as e:
        raise OptimizationError(
            'VRP optimization failed',
            method='vrp',
            details={'error': str(e)}
        )


@api_bp.route('/optimize/hybrid-vrp', methods=['POST'])
@handle_domain_exceptions
def optimize_hybrid_vrp():
    """Run Hybrid VRP optimization (classical VRP + quantum enhancement)"""
    data = request.get_json(silent=True)
    if not data:
        raise ValidationError('No data provided')
    
    try:
        result = optimization_service.run_hybrid_vrp_optimization(data)
        return success_response(
            {'method': 'hybrid_vrp', 'result': result},
            message='Hybrid VRP optimization completed'
        )
    except Exception as e:
        raise OptimizationError(
            'Hybrid VRP optimization failed',
            method='hybrid_vrp',
            details={'error': str(e)}
        )


@api_bp.route('/optimize/status/<job_id>', methods=['GET'])
def optimization_status(job_id):
    """Get optimization job status"""
    try:
        status = optimization_service.get_job_status(job_id)
        return success_response(status)
    except Exception as e:  # pragma: no cover
        return error_response(
            'STATUS_ERROR', 'Failed to get status', details=str(e), status=500
        )


# Data management endpoints
@api_bp.route('/data/warehouses', methods=['GET', 'POST'])
@handle_domain_exceptions
def warehouses():
    """Manage warehouse data"""
    if request.method == 'GET':
        warehouses = data_service.get_warehouses()
        return success_response(warehouses)
    elif request.method == 'POST':
        data = request.get_json()
        result = data_service.create_warehouse(data)
        resp, code = success_response(
            result, message='Warehouse created', status=201
        )
        return resp, code


@api_bp.route('/data/customers', methods=['GET', 'POST'])
@handle_domain_exceptions
def customers():
    """Manage customer data"""
    if request.method == 'GET':
        customers = data_service.get_customers()
        return success_response(customers)
    elif request.method == 'POST':
        data = request.get_json()
        result = data_service.create_customer(data)
        resp, code = success_response(
            result, message='Customer created', status=201
        )
        return resp, code


@api_bp.route('/data/routes', methods=['GET', 'POST'])
@handle_domain_exceptions
def routes():
    """Manage route data"""
    if request.method == 'GET':
        routes = data_service.get_routes()
        return success_response(routes)
    elif request.method == 'POST':
        data = request.get_json()
        result = data_service.create_route(data)
        resp, code = success_response(
            result, message='Route created', status=201
        )
        return resp, code


@api_bp.route('/data/upload', methods=['POST'])
@handle_domain_exceptions
def upload_data():
    """Upload CSV datasets"""
    if 'file' not in request.files:
        raise ValidationError('No file provided')
    
    file = request.files['file']
    data_type = request.form.get('type', 'warehouses')
    
    result = data_service.process_upload(file, data_type)
    return success_response(result, message='File processed successfully')


@api_bp.route('/data/validate', methods=['POST'])
@handle_domain_exceptions
def validate_data():
    """Validate supply chain data"""
    data = request.get_json(silent=True)
    if not data:
        raise ValidationError('No data provided for validation')
    
    validation_result = data_service.validate_data(data)
    # Convert Pydantic model to dict for JSON serialization
    result_dict = validation_result.model_dump() if hasattr(validation_result, 'model_dump') else validation_result.dict()
    return success_response(
        result_dict, message='Validation completed'
    )


@api_bp.route('/data/<data_type>', methods=['DELETE'])
@handle_domain_exceptions
def delete_data(data_type):
    """Delete specific data type"""
    valid_types = ['warehouses', 'customers', 'routes']
    if data_type not in valid_types:
        raise ValidationError(
            f'Invalid data type. Must be one of: {valid_types}'
        )
    
    result = data_service.delete_data(data_type)
    return success_response(result, message='Data deleted successfully')


@api_bp.route('/data/sample', methods=['GET'])
def get_sample_data():
    """Get sample data for testing"""
    try:
        sample_data = data_service.get_sample_data()
        return success_response(sample_data)
    except Exception as e:  # pragma: no cover
        return error_response(
            'SAMPLE_DATA_ERROR', 'Failed to get sample data',
            details=str(e), status=500
        )


# Results endpoints
@api_bp.route('/results/<result_id>', methods=['GET'])
def get_result(result_id):
    """Get optimization result by ID"""
    try:
        result = optimization_service.get_result(result_id)
        if not result:
            return error_response(
                'RESULT_NOT_FOUND', 'Result not found', status=404
            )
        return success_response(result)
    except Exception as e:  # pragma: no cover
        return error_response(
            'RESULT_ERROR', 'Failed to get result', details=str(e), status=500
        )


@api_bp.route('/results', methods=['GET'])
def list_results():
    """List recent optimization results"""
    try:
        limit = request.args.get('limit', 10, type=int)
        results = optimization_service.list_results(limit=limit)
        return success_response(results)
    except Exception as e:  # pragma: no cover
        return error_response(
            'RESULTS_LIST_ERROR', 'Failed to list results',
            details=str(e), status=500
        )


# Dashboard aggregation endpoint
@api_bp.route('/dashboard', methods=['GET'])
@handle_domain_exceptions
def dashboard():
    """Return aggregated metrics for dashboard view.

    This keeps it simple for now: counts of entities and latest results.
    Extend later with performance metrics, inventory levels, etc.
    """
    warehouses = data_service.get_warehouses()
    customers = data_service.get_customers()
    routes_data = data_service.get_routes()
    
    # Get recent results from optimization service if available
    recent_results = []
    if hasattr(optimization_service, 'get_recent_results'):
        recent_results = optimization_service.get_recent_results(limit=5)
    elif hasattr(optimization_service, 'results_store'):
        # For simple OptimizationService, get from in-memory store
        recent_results = list(optimization_service.results_store.values())[-5:]

    payload = {
        'summary': {
            'warehouses': len(warehouses or []),
            'customers': len(customers or []),
            'routes': len(routes_data or []),
            'recentOptimizations': len(recent_results or []),
        },
        'recentResults': recent_results,
        'metrics': {
            'totalCost': sum(r.get('totalCost', 0) for r in recent_results),
            'totalCo2': sum(r.get('totalCo2', 0) for r in recent_results),
            'avgOptimizationTime': sum(r.get('optimization_time', 0) for r in recent_results) / max(len(recent_results), 1)
        },
        # Include actual data for map visualization
        'warehouses': warehouses or [],
        'customers': customers or [],
        'routes': routes_data or [],
    }
    return success_response(payload)
