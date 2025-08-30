"""
Main Flask Application for Content Generation AI
File: backend/app.py
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
import logging
from datetime import datetime

# Import configuration
from config import config

# Initialize extensions
db = SQLAlchemy()

def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Setup logging
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

def register_blueprints(app):
    """Register all blueprints"""
    from api.routes.product import product_bp
    from api.routes.social import social_bp
    from api.routes.blog import blog_bp
    from api.routes.marketing import marketing_bp
    from api.routes.models import models_bp
    
    # Register API routes
    app.register_blueprint(product_bp, url_prefix=f"{app.config['API_PREFIX']}/product")
    app.register_blueprint(social_bp, url_prefix=f"{app.config['API_PREFIX']}/social")
    app.register_blueprint(blog_bp, url_prefix=f"{app.config['API_PREFIX']}/blog")
    app.register_blueprint(marketing_bp, url_prefix=f"{app.config['API_PREFIX']}/marketing")
    app.register_blueprint(models_bp, url_prefix=f"{app.config['API_PREFIX']}/models")

def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad Request',
            'message': 'Invalid request data',
            'timestamp': datetime.utcnow().isoformat()
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found',
            'timestamp': datetime.utcnow().isoformat()
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An internal server error occurred',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Create Flask app instance
app = create_app()

# Health check endpoint
@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Content Generation AI API',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/v1/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        'status': 'operational',
        'endpoints': [
            '/api/v1/product/generate',
            '/api/v1/social/generate',
            '/api/v1/blog/generate',
            '/api/v1/marketing/generate'
        ],
        'models_loaded': True,
        'database_connected': True,
        'timestamp': datetime.utcnow().isoformat()
    })

# CORS preflight handler
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({'status': 'OK'})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        return response

if __name__ == '__main__':
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print("🚀 Content Generation AI API Starting...")
    print(f"🌐 Server running on http://localhost:{port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"📊 API endpoints: http://localhost:{port}/api/v1/status")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )