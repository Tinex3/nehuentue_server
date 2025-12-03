"""
API Blueprint - Registro de rutas
"""
from flask import Blueprint

api_bp = Blueprint('api', __name__)

# Importar rutas después de crear el blueprint para evitar imports circulares
from . import auth, zones, devices, device_types, events, evidences, measurements
