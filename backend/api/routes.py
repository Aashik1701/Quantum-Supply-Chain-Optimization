"""
Main API routes for Hybrid Quantum-Classical Supply Chain Optimization
"""

from flask import Blueprint, request
from utils.response import success_response, error_response
from services.optimization_service import OptimizationService
from services.data_service import DataService
from utils.validators import validate_optimization_request

api_bp = Blueprint('api', __name__)

# Initialize services
optimization_service = OptimizationService()
data_service = DataService()


@api_bp.route('/health', methods=['GET'])
def health():
    """API health check"""
    return success_response({'status': 'healthy', 'service': 'api'})


# Optimization endpoints
@api_bp.route('/optimize', methods=['POST'])
def optimize():
    """Generic optimization dispatcher endpoint"""
    try:
        data = request.get_json()
        if not data:
            return error_response(
                'VALIDATION_ERROR', 'No data provided', status=400
            )
        
        method = data.get('method', 'hybrid').lower()
        
        # Route to specific optimization method
        if method == 'classical':
            return _run_classical_optimization(data)
        elif method == 'quantum':
            return _run_quantum_optimization(data)
        elif method == 'hybrid':
            return _run_hybrid_optimization(data)
        else:
            return error_response(
                'INVALID_METHOD',
                f'Invalid method: {method}. Expected classical/quantum/hybrid',
                status=400
            )
    except Exception as e:  # pragma: no cover
        return error_response(
            'OPTIMIZATION_ERROR', 'Optimization dispatcher failed',
            details=str(e), status=500
        )


def _run_classical_optimization(data):
    """Internal classical optimization logic"""
    if not validate_optimization_request(data):
        return error_response(
            'VALIDATION_ERROR', 'Invalid input data', status=400
        )
    
    result = optimization_service.run_classical_optimization(data)
    return success_response(
        {'method': 'classical', 'result': result},
        message='Optimization completed'
    )


def _run_quantum_optimization(data):
    """Internal quantum optimization logic"""
    if not validate_optimization_request(data):
        return error_response(
            'VALIDATION_ERROR', 'Invalid input data', status=400
        )
    
    result = optimization_service.run_quantum_optimization(data)
    return success_response(
        {'method': 'quantum', 'result': result},
        message='Optimization completed'
    )


def _run_hybrid_optimization(data):
    """Internal hybrid optimization logic"""
    if not validate_optimization_request(data):
        return error_response(
            'VALIDATION_ERROR', 'Invalid input data', status=400
        )
    
    result = optimization_service.run_hybrid_optimization(data)
    return success_response(
        {'method': 'hybrid', 'result': result},
        message='Optimization completed'
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
def upload_data():
    """Upload CSV datasets"""
    try:
        if 'file' not in request.files:
            return error_response(
                'UPLOAD_ERROR', 'No file provided', status=400
            )
        file = request.files['file']
        data_type = request.form.get('type', 'warehouses')
        result = data_service.process_upload(file, data_type)
        return success_response(result, message='File processed')
    except Exception as e:  # pragma: no cover
        return error_response(
            'UPLOAD_ERROR', 'Upload failed', details=str(e), status=500
        )


@api_bp.route('/data/validate', methods=['POST'])
def validate_data():
    """Validate supply chain data"""
    try:
        data = request.get_json()
        if not data:
            return error_response(
                'VALIDATION_ERROR', 'No data provided', status=400
            )
        validation_result = data_service.validate_data(data)
        return success_response(
            validation_result, message='Validation completed'
        )
    except Exception as e:  # pragma: no cover
        return error_response(
            'VALIDATION_ERROR', 'Validation failed', details=str(e), status=500
        )


@api_bp.route('/data/<data_type>', methods=['DELETE'])
def delete_data(data_type):
    """Delete specific data type"""
    try:
        valid_types = ['warehouses', 'customers', 'routes']
        if data_type not in valid_types:
            return error_response(
                'INVALID_DATA_TYPE',
                f'Invalid data type. Must be one of: {valid_types}',
                status=400
            )
        result = data_service.delete_data(data_type)
        return success_response(result, message='Data deleted')
    except Exception as e:  # pragma: no cover
        return error_response(
            'DELETE_FAILED', 'Delete failed', details=str(e), status=500
        )


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
def dashboard():
    """Return aggregated metrics for dashboard view.

    This keeps it simple for now: counts of entities and latest results.
    Extend later with performance metrics, inventory levels, etc.
    """
    try:
        warehouses = data_service.get_warehouses()
        customers = data_service.get_customers()
        routes_data = data_service.get_routes()
        recent_results = optimization_service.list_results(limit=5)

        payload = {
            'summary': {
                'warehouses': len(warehouses or []),
                'customers': len(customers or []),
                'routes': len(routes_data or []),
                'recentOptimizations': len(recent_results or []),
            },
            'recentResults': recent_results,
        }
        return success_response(payload)
    except Exception as e:  # pragma: no cover
        return error_response(
            'DASHBOARD_ERROR', 'Failed to build dashboard data',
            details=str(e), status=500
        )
