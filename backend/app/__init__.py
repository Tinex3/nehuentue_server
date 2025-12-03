"""
Sistema de Seguridad IoT - Backend Flask
"""
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from .config import Config
from .extensions import db, migrate, jwt, ma
from .api import api_bp


def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)
    
    # CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost", "http://localhost:3000", "http://localhost:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "PATCH"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Registrar blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Health check
    @app.route('/api/health')
    def health():
        return {'status': 'healthy', 'service': 'iot-backend'}
    
    return app
