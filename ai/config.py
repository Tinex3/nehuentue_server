"""
Configuración del Servicio de IA
"""
import os


class Config:
    # Modelo
    MODEL_PATH = os.environ.get('MODEL_PATH', '/app/models/detect.tflite')
    LABELS_PATH = os.environ.get('LABELS_PATH', '/app/models/labels.txt')
    
    # Detección
    CONFIDENCE_THRESHOLD = float(os.environ.get('CONFIDENCE_THRESHOLD', 0.5))
    DETECT_PERSONS_ONLY = os.environ.get('DETECT_PERSONS_ONLY', 'false').lower() == 'true'
    
    # Tamaño de entrada del modelo (MobileNet SSD)
    INPUT_SIZE = int(os.environ.get('INPUT_SIZE', 300))
    
    # Base de datos
    DATABASE_URL = os.environ.get(
        'DATABASE_URL',
        'postgresql://iot_user:iot_password@localhost:5432/iot_security'
    )
    
    # Evidencias
    EVIDENCES_PATH = os.environ.get('EVIDENCES_PATH', '/app/evidences')


config = Config()
