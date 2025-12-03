"""
Servicio de IA - Detección de objetos/personas
Sistema de Seguridad IoT
"""
import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

from config import config
from detector import ObjectDetector
from database import Database

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ai-service')

# Crear app Flask
app = Flask(__name__)
CORS(app)

# Inicializar componentes
detector = None
db = None


def init_components():
    """Inicializar detector y base de datos"""
    global detector, db
    
    logger.info("Inicializando servicio de IA...")
    
    # Inicializar detector
    detector = ObjectDetector(
        model_path=config.MODEL_PATH,
        labels_path=config.LABELS_PATH,
        confidence_threshold=config.CONFIDENCE_THRESHOLD
    )
    
    # Inicializar BD
    db = Database()
    db.connect()
    
    logger.info("Servicio de IA inicializado")


@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'iot-ai',
        'model_loaded': detector is not None and detector.is_loaded()
    })


@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Analizar imagen para detectar objetos/personas
    
    Request JSON:
    {
        "evidence_id": 123,
        "file_path": "2024-01-01/zone_1/cam1_120000.jpg"
    }
    
    O multipart con archivo:
    - file: imagen
    - evidence_id: (opcional)
    """
    try:
        # Obtener imagen
        if request.is_json:
            data = request.json
            evidence_id = data.get('evidence_id')
            file_path = data.get('file_path')
            
            if not file_path:
                return jsonify({'error': 'file_path requerido'}), 400
            
            # Construir ruta completa
            full_path = os.path.join(config.EVIDENCES_PATH, file_path)
            
            if not os.path.exists(full_path):
                return jsonify({'error': 'Archivo no encontrado'}), 404
            
            image_path = full_path
            
        elif 'file' in request.files:
            # Archivo subido directamente
            file = request.files['file']
            evidence_id = request.form.get('evidence_id')
            
            # Guardar temporalmente
            import tempfile
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            file.save(temp_file.name)
            image_path = temp_file.name
        else:
            return jsonify({'error': 'Se requiere file_path o archivo'}), 400
        
        # Ejecutar detección
        logger.info(f"Analizando imagen: {image_path}")
        results = detector.detect(image_path)
        
        # Filtrar solo personas si está configurado
        if config.DETECT_PERSONS_ONLY:
            results['detections'] = [
                d for d in results['detections'] 
                if d['class'] == 'person'
            ]
        
        # Actualizar evidencia en BD si hay evidence_id
        if evidence_id and db:
            db.update_evidence_ai_metadata(evidence_id, results)
            logger.info(f"Evidencia {evidence_id} actualizada con resultados IA")
        
        return jsonify({
            'success': True,
            'evidence_id': evidence_id,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error en análisis: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/detect', methods=['POST'])
def detect_realtime():
    """
    Detección en tiempo real (sin guardar en BD)
    Recibe imagen como multipart
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Archivo requerido'}), 400
        
        file = request.files['file']
        
        # Leer imagen directamente en memoria
        import numpy as np
        import cv2
        
        file_bytes = np.frombuffer(file.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({'error': 'Imagen inválida'}), 400
        
        # Detectar
        results = detector.detect_from_array(image)
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error en detección: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/model/info', methods=['GET'])
def model_info():
    """Información del modelo cargado"""
    if detector is None:
        return jsonify({'error': 'Modelo no cargado'}), 503
    
    return jsonify(detector.get_model_info())


# Inicializar al cargar
with app.app_context():
    init_components()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
