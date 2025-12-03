"""
Configuración del Worker
"""
import os


class Config:
    # Base de datos
    DATABASE_URL = os.environ.get(
        'DATABASE_URL',
        'postgresql://iot_user:iot_password@localhost:5432/iot_security'
    )
    
    # MQTT
    MQTT_BROKER = os.environ.get('MQTT_BROKER', 'localhost')
    MQTT_PORT = int(os.environ.get('MQTT_PORT', 1883))
    MQTT_USER = os.environ.get('MQTT_USER', 'worker')
    MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD', 'worker123')
    MQTT_CLIENT_ID = os.environ.get('MQTT_CLIENT_ID', 'iot-worker')
    
    # Tópicos MQTT a suscribir
    MQTT_TOPICS = [
        ('events/motion', 1),           # Eventos de movimiento PIR
        ('devices/+/status', 1),        # Estado de dispositivos
        ('devices/+/telemetry', 1),     # Telemetría
        ('cameras/+/frame', 1),         # Frames de cámaras
    ]
    
    # Backend API
    BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:5000')
    
    # Servicio IA
    AI_SERVICE_URL = os.environ.get('AI_SERVICE_URL', 'http://localhost:5001')
    
    # Evidencias
    EVIDENCES_PATH = os.environ.get('EVIDENCES_PATH', '/app/evidences')
    
    # Reglas
    MOTION_COOLDOWN_SECONDS = int(os.environ.get('MOTION_COOLDOWN_SECONDS', 30))
    AUTO_LIGHTS_DURATION = int(os.environ.get('AUTO_LIGHTS_DURATION', 300))
    CAPTURE_FRAMES_ON_MOTION = int(os.environ.get('CAPTURE_FRAMES_ON_MOTION', 5))


config = Config()
