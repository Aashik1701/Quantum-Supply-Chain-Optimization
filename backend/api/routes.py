"""
Main API routes for Hybrid Quantum-Classical Supply Chain Optimization
"""

from flask import Blueprint, request, jsonify
from services.optimization_service import OptimizationService
from services.data_service import DataService
from utils.validators import validate_optimization_request
import traceback

api_bp = Blueprint('api', __name__)

# Initialize services
optimization_service = OptimizationService()
data_service = DataService()


@api_bp.route('/health', methods=['GET'])
def health():
    """API health check"""
    return jsonify({'status': 'healthy', 'service': 'api'})


# Optimization endpoints
@api_bp.route('/optimize/classical', methods=['POST'])
def optimize_classical():
    """Run classical optimization"""
    try:
        data = request.get_json()
        
        # Validate input
        if not validate_optimization_request(data):
            return jsonify({'error': 'Invalid input data'}), 400
        
        # Run optimization
        result = optimization_service.run_classical_optimization(data)
        
        return jsonify({
            'success': True,
            'method': 'classical',
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Optimization failed: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500


@api_bp.route('/optimize/quantum', methods=['POST'])
def optimize_quantum():
    """Run quantum optimization (QAOA)"""
    try:
        data = request.get_json()
        
        # Validate input
        if not validate_optimization_request(data):
            return jsonify({'error': 'Invalid input data'}), 400
        
        # Run optimization
        result = optimization_service.run_quantum_optimization(data)
        
        return jsonify({
            'success': True,
            'method': 'quantum',
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Quantum optimization failed: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500


@api_bp.route('/optimize/hybrid', methods=['POST'])
def optimize_hybrid():
    """Run hybrid quantum-classical optimization"""
    try:
        data = request.get_json()
        
        # Validate input
        if not validate_optimization_request(data):
            return jsonify({'error': 'Invalid input data'}), 400
        
        # Run optimization
        result = optimization_service.run_hybrid_optimization(data)
        
        return jsonify({
            'success': True,
            'method': 'hybrid',
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Hybrid optimization failed: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500


@api_bp.route('/optimize/status/<job_id>', methods=['GET'])
def optimization_status(job_id):
    """Get optimization job status"""
    try:
        status = optimization_service.get_job_status(job_id)
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': f'Failed to get status: {str(e)}'}), 500


# Data management endpoints
@api_bp.route('/data/warehouses', methods=['GET', 'POST'])
def warehouses():
    """Manage warehouse data"""
    if request.method == 'GET':
        warehouses = data_service.get_warehouses()
        return jsonify(warehouses)
    
    elif request.method == 'POST':
        data = request.get_json()
        result = data_service.create_warehouse(data)
        return jsonify(result), 201


@api_bp.route('/data/customers', methods=['GET', 'POST'])
def customers():
    """Manage customer data"""
    if request.method == 'GET':
        customers = data_service.get_customers()
        return jsonify(customers)
    
    elif request.method == 'POST':
        data = request.get_json()
        result = data_service.create_customer(data)
        return jsonify(result), 201


@api_bp.route('/data/routes', methods=['GET', 'POST'])
def routes():
    """Manage route data"""
    if request.method == 'GET':
        routes = data_service.get_routes()
        return jsonify(routes)
    
    elif request.method == 'POST':
        data = request.get_json()
        result = data_service.create_route(data)
        return jsonify(result), 201


@api_bp.route('/data/upload', methods=['POST'])
def upload_data():
    """Upload CSV datasets"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        data_type = request.form.get('type', 'warehouses')
        
        result = data_service.process_upload(file, data_type)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500


@api_bp.route('/data/sample', methods=['GET'])
def get_sample_data():
    """Get sample data for testing"""
    try:
        sample_data = data_service.get_sample_data()
        return jsonify(sample_data)
    except Exception as e:
        return jsonify({'error': f'Failed to get sample data: {str(e)}'}), 500


# Results endpoints
@api_bp.route('/results/<result_id>', methods=['GET'])
def get_result(result_id):
    """Get optimization result by ID"""
    try:
        result = optimization_service.get_result(result_id)
        if not result:
            return jsonify({'error': 'Result not found'}), 404
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Failed to get result: {str(e)}'}), 500


@api_bp.route('/results', methods=['GET'])
def list_results():
    """List recent optimization results"""
    try:
        limit = request.args.get('limit', 10, type=int)
        results = optimization_service.list_results(limit=limit)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': f'Failed to list results: {str(e)}'}), 500
