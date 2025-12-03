"""
Detector de objetos usando TFLite
"""
import os
import logging
import numpy as np
import cv2
from typing import List, Dict, Any, Optional

logger = logging.getLogger('ai-service.detector')

# Intentar importar TFLite
try:
    import tflite_runtime.interpreter as tflite
    TFLITE_AVAILABLE = True
except ImportError:
    try:
        import tensorflow.lite as tflite
        TFLITE_AVAILABLE = True
    except ImportError:
        TFLITE_AVAILABLE = False
        logger.warning("TFLite no disponible, usando detector simulado")


class ObjectDetector:
    """
    Detector de objetos usando modelo TFLite (MobileNet SSD)
    """
    
    # Labels por defecto para COCO dataset
    DEFAULT_LABELS = [
        'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck',
        'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench',
        'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra',
        'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
        'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
        'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
        'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange',
        'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
        'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse',
        'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
        'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
        'toothbrush'
    ]
    
    def __init__(self, model_path: str, labels_path: str = None, 
                 confidence_threshold: float = 0.5, input_size: int = 300):
        self.model_path = model_path
        self.labels_path = labels_path
        self.confidence_threshold = confidence_threshold
        self.input_size = input_size
        
        self.interpreter = None
        self.labels = []
        self.input_details = None
        self.output_details = None
        
        self._load_model()
        self._load_labels()
    
    def _load_model(self):
        """Cargar modelo TFLite"""
        if not TFLITE_AVAILABLE:
            logger.warning("TFLite no disponible")
            return
        
        if not os.path.exists(self.model_path):
            logger.warning(f"Modelo no encontrado: {self.model_path}")
            return
        
        try:
            self.interpreter = tflite.Interpreter(model_path=self.model_path)
            self.interpreter.allocate_tensors()
            
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            
            # Obtener tamaño de entrada del modelo
            input_shape = self.input_details[0]['shape']
            self.input_size = input_shape[1]
            
            logger.info(f"Modelo cargado: {self.model_path}")
            logger.info(f"Input shape: {input_shape}")
            
        except Exception as e:
            logger.error(f"Error cargando modelo: {e}")
            self.interpreter = None
    
    def _load_labels(self):
        """Cargar etiquetas"""
        if self.labels_path and os.path.exists(self.labels_path):
            with open(self.labels_path, 'r') as f:
                self.labels = [line.strip() for line in f.readlines()]
            logger.info(f"Labels cargados: {len(self.labels)}")
        else:
            self.labels = self.DEFAULT_LABELS
            logger.info("Usando labels por defecto (COCO)")
    
    def is_loaded(self) -> bool:
        """Verificar si el modelo está cargado"""
        return self.interpreter is not None
    
    def detect(self, image_path: str) -> Dict[str, Any]:
        """
        Detectar objetos en una imagen desde archivo
        
        Returns:
            {
                'detections': [
                    {'class': 'person', 'confidence': 0.95, 'bbox': [x1, y1, x2, y2]},
                    ...
                ],
                'image_size': [width, height],
                'persons_detected': 2
            }
        """
        # Leer imagen
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"No se pudo leer imagen: {image_path}")
        
        return self.detect_from_array(image)
    
    def detect_from_array(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Detectar objetos en una imagen (numpy array)
        """
        original_height, original_width = image.shape[:2]
        
        # Si no hay modelo, usar detección simulada
        if not self.is_loaded():
            return self._simulated_detection(original_width, original_height)
        
        # Preprocesar imagen
        input_image = self._preprocess(image)
        
        # Ejecutar inferencia
        self.interpreter.set_tensor(self.input_details[0]['index'], input_image)
        self.interpreter.invoke()
        
        # Obtener resultados
        # El formato depende del modelo, típicamente:
        # - boxes: [1, num_detections, 4]
        # - classes: [1, num_detections]
        # - scores: [1, num_detections]
        boxes = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
        classes = self.interpreter.get_tensor(self.output_details[1]['index'])[0]
        scores = self.interpreter.get_tensor(self.output_details[2]['index'])[0]
        
        # Procesar detecciones
        detections = []
        for i in range(len(scores)):
            if scores[i] >= self.confidence_threshold:
                class_id = int(classes[i])
                class_name = self.labels[class_id] if class_id < len(self.labels) else f'class_{class_id}'
                
                # Convertir bbox a coordenadas absolutas
                ymin, xmin, ymax, xmax = boxes[i]
                bbox = [
                    int(xmin * original_width),
                    int(ymin * original_height),
                    int(xmax * original_width),
                    int(ymax * original_height)
                ]
                
                detections.append({
                    'class': class_name,
                    'class_id': class_id,
                    'confidence': float(scores[i]),
                    'bbox': bbox
                })
        
        # Ordenar por confianza
        detections.sort(key=lambda x: x['confidence'], reverse=True)
        
        persons_detected = sum(1 for d in detections if d['class'] == 'person')
        
        return {
            'detections': detections,
            'image_size': [original_width, original_height],
            'persons_detected': persons_detected,
            'total_detections': len(detections)
        }
    
    def _preprocess(self, image: np.ndarray) -> np.ndarray:
        """Preprocesar imagen para el modelo"""
        # Redimensionar
        resized = cv2.resize(image, (self.input_size, self.input_size))
        
        # Convertir BGR a RGB
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        
        # Normalizar según el tipo de entrada del modelo
        input_dtype = self.input_details[0]['dtype']
        
        if input_dtype == np.uint8:
            input_image = np.expand_dims(rgb, axis=0).astype(np.uint8)
        else:
            # Float, normalizar a [0, 1] o [-1, 1]
            input_image = np.expand_dims(rgb, axis=0).astype(np.float32) / 255.0
        
        return input_image
    
    def _simulated_detection(self, width: int, height: int) -> Dict[str, Any]:
        """Detección simulada cuando no hay modelo"""
        import random
        
        # Simular 0-2 personas detectadas
        num_persons = random.randint(0, 2)
        detections = []
        
        for i in range(num_persons):
            # Generar bbox aleatorio
            x1 = random.randint(0, width // 2)
            y1 = random.randint(0, height // 2)
            x2 = random.randint(x1 + 50, min(x1 + 200, width))
            y2 = random.randint(y1 + 100, min(y1 + 400, height))
            
            detections.append({
                'class': 'person',
                'class_id': 0,
                'confidence': random.uniform(0.7, 0.99),
                'bbox': [x1, y1, x2, y2],
                'simulated': True
            })
        
        return {
            'detections': detections,
            'image_size': [width, height],
            'persons_detected': num_persons,
            'total_detections': num_persons,
            'simulated': True
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Obtener información del modelo"""
        info = {
            'model_path': self.model_path,
            'labels_count': len(self.labels),
            'confidence_threshold': self.confidence_threshold,
            'input_size': self.input_size,
            'loaded': self.is_loaded()
        }
        
        if self.is_loaded():
            info['input_details'] = str(self.input_details)
            info['output_details'] = str(self.output_details)
        
        return info
