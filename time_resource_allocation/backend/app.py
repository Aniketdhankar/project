"""
Main Flask Application
Entry point for the Time & Resource Allocation System
"""

from flask import Flask, jsonify
from flask_cors import CORS
import logging
from pathlib import Path

from config.config import get_config
from routes.api import api
from routes.websocket import websocket_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_name=None):
    """
    Application factory
    
    Args:
        config_name: Configuration environment name
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    logger.info(f"Starting application with {config.__class__.__name__}")
    
    # Initialize CORS
    CORS(app, origins=app.config.get('CORS_ORIGINS', ['*']))
    
    # Initialize database
    # NOTE: Uncomment when database models are ready
    # from models.models import db
    # db.init_app(app)
    # 
    # with app.app_context():
    #     db.create_all()
    
    # Register blueprints
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(websocket_bp, url_prefix='/api')
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register health check
    @app.route('/')
    def index():
        return jsonify({
            'name': 'Time & Resource Allocation System API',
            'version': '1.0.0',
            'status': 'running'
        })
    
    logger.info("Application initialized successfully")
    return app


def register_error_handlers(app):
    """Register error handlers for the application"""
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not found',
            'message': 'The requested resource was not found'
        }), 404
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad request',
            'message': str(error)
        }), 400
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.error(f"Unhandled exception: {str(error)}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500


# Create application instance
app = create_app()


if __name__ == '__main__':
    # Run the application
    # In production, use a WSGI server like gunicorn
    port = int(app.config.get('PORT', 5000))
    debug = app.config.get('DEBUG', False)
    
    logger.info(f"Starting Flask server on port {port} (debug={debug})")
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
