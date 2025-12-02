"""Main Flask application for Hybrid Quantum-Classical Supply Chain API"""

import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from werkzeug.middleware.proxy_fix import ProxyFix

from config.config import Config
from config.database import init_db
from api.routes import api_bp
from utils.response import error_response
from api.websocket import socketio_events


def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    # Initialize database
    init_db()
    # Initialize extensions
    CORS(app, origins=app.config.get(
        'CORS_ORIGINS', ['http://localhost:3000']
    ))
    # Enable Redis message queue for cross-process emits (worker -> server)
    redis_url = os.environ.get('REDIS_URL')
    socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        async_mode='threading',
        message_queue=redis_url if redis_url else None,
    )
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    # Global error handlers
    @app.errorhandler(404)
    def not_found(_):  # pragma: no cover
        return error_response('NOT_FOUND', 'Resource not found', status=404)

    @app.errorhandler(400)
    def bad_request(e):  # pragma: no cover
        msg = getattr(e, 'description', 'Bad request')
        return error_response('BAD_REQUEST', msg, status=400)

    @app.errorhandler(500)
    def internal_error(e):  # pragma: no cover
        return error_response(
            'INTERNAL_ERROR', 'Internal server error',
            details=str(e), status=500
        )

    @app.errorhandler(Exception)
    def unhandled_exception(e):  # pragma: no cover
        return error_response(
            'UNHANDLED_EXCEPTION', 'Unhandled exception',
            details=str(e), status=500
        )
    # Register WebSocket events
    socketio_events(socketio)
    # Initialize routes with socketio
    from api.routes import init_routes
    init_routes(socketio)
    # Middleware for production
    if app.config.get('ENV') == 'production':
        app.wsgi_app = ProxyFix(
            app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
        )
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'version': app.config.get('VERSION', '1.0.0'),
            'environment': app.config.get('ENV', 'development')
        })
    return app, socketio


if __name__ == '__main__':
    app, socketio = create_app()
    # Development server
    debug = os.environ.get('FLASK_ENV') == 'development'
    # Use 5000 by default to align with docker-compose and local proxy config
    port = int(os.environ.get('PORT', 5000))
    socketio.run(
        app,
        debug=debug,
        host='0.0.0.0',
        port=port,
        allow_unsafe_werkzeug=True  # Only for development
    )
