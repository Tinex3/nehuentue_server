"""
Configuración de la aplicación Flask
"""
import os
from datetime import timedelta


class Config:
    """Configuración base"""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://iot_user:iot_password@localhost:5432/iot_security'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # MQTT
    MQTT_BROKER = os.environ.get('MQTT_BROKER', 'localhost')
    MQTT_PORT = int(os.environ.get('MQTT_PORT', 1883))
    MQTT_USER = os.environ.get('MQTT_USER', 'backend')
    MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD', 'backend123')
    
    # Servicio IA
    AI_SERVICE_URL = os.environ.get('AI_SERVICE_URL', 'http://localhost:5001')
    
    # Archivos
    EVIDENCES_PATH = os.environ.get('EVIDENCES_PATH', '/app/evidences')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload


class DevelopmentConfig(Config):
    """Configuración de desarrollo"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Configuración de producción"""
    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Configuración de pruebas"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
