"""
Handler de frames de cámara
Implementa RF6 - Almacenamiento de evidencias
"""
import os
import json
import logging
import requests
from datetime import datetime
from pathlib import Path

from config import config

logger = logging.getLogger('worker.handlers.camera')


def handle_camera_frame(db, camera_id: str, data, raw_payload: bytes):
    """
    Procesa frames recibidos de cámaras
    
    El payload puede ser:
    1. JSON con metadata y frame en base64
    2. Binario puro (imagen JPEG)
    
    Payload JSON esperado:
    {
        "event_id": 123,        // opcional, asocia a evento existente
        "zone_id": 1,           // opcional
        "timestamp": "...",
        "frame": "base64...",   // imagen en base64
        "format": "jpeg"
    }
    """
    try:
        camera_id_int = int(camera_id)
        
        # Obtener info de la cámara
        camera = db.get_device_by_id(camera_id_int)
        if not camera:
            logger.warning(f"Cámara {camera_id} no encontrada")
            return
        
        zone_id = camera.get('zone_id')
        
        # Determinar si es JSON o binario
        if isinstance(data, dict):
            # JSON con metadata
            event_id = data.get('event_id')
            zone_id = data.get('zone_id', zone_id)
            timestamp = data.get('timestamp', datetime.utcnow().isoformat())
            
            # Decodificar frame de base64
            import base64
            frame_b64 = data.get('frame')
            if frame_b64:
                image_data = base64.b64decode(frame_b64)
            else:
                logger.warning(f"Frame vacío de cámara {camera_id}")
                return
        else:
            # Binario puro
            image_data = raw_payload
            event_id = None
            timestamp = datetime.utcnow().isoformat()
        
        # Guardar imagen en disco
        file_path = _save_image(camera_id_int, zone_id, image_data, timestamp)
        
        if not file_path:
            return
        
        # Si no hay event_id, crear evento de captura
        if not event_id:
            event_id = db.create_event(
                device_id=camera_id_int,
                zone_id=zone_id,
                event_type='capture',
                payload={'source': 'camera_frame', 'timestamp': timestamp}
            )
        
        # Crear evidencia en BD
        evidence_id = db.create_evidence(
            device_id=camera_id_int,
            zone_id=zone_id,
            event_id=event_id,
            file_path=file_path
        )
        
        logger.info(f"[CAMERA] Frame guardado - Cámara: {camera_id}, Evidencia: {evidence_id}")
        
        # Enviar a servicio de IA (async)
        _send_to_ai_service(evidence_id, file_path)
        
    except ValueError:
        logger.warning(f"camera_id inválido: {camera_id}")
    except Exception as e:
        logger.error(f"Error procesando frame de cámara: {e}", exc_info=True)


def _save_image(camera_id: int, zone_id: int, image_data: bytes, timestamp: str) -> str:
    """
    Guarda imagen en disco y retorna la ruta relativa
    """
    try:
        # Crear estructura de directorios: evidences/YYYY-MM-DD/zone_X/
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        date_dir = dt.strftime('%Y-%m-%d')
        zone_dir = f"zone_{zone_id}" if zone_id else "no_zone"
        
        base_path = Path(config.EVIDENCES_PATH)
        target_dir = base_path / date_dir / zone_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Nombre de archivo único
        filename = f"cam{camera_id}_{dt.strftime('%H%M%S_%f')}.jpg"
        file_path = target_dir / filename
        
        # Guardar imagen
        with open(file_path, 'wb') as f:
            f.write(image_data)
        
        # Retornar ruta relativa
        relative_path = str(file_path.relative_to(base_path))
        logger.debug(f"Imagen guardada: {relative_path}")
        
        return relative_path
        
    except Exception as e:
        logger.error(f"Error guardando imagen: {e}")
        return None


def _send_to_ai_service(evidence_id: int, file_path: str):
    """
    Envía imagen al servicio de IA para análisis (RF7)
    """
    try:
        ai_url = f"{config.AI_SERVICE_URL}/analyze"
        
        # Enviar solicitud async (no bloquear)
        payload = {
            'evidence_id': evidence_id,
            'file_path': file_path
        }
        
        # Timeout corto, el servicio procesará async
        requests.post(ai_url, json=payload, timeout=2)
        logger.debug(f"Imagen enviada a IA: {evidence_id}")
        
    except requests.exceptions.Timeout:
        # Es esperado, el servicio procesa async
        pass
    except requests.exceptions.ConnectionError:
        logger.warning("Servicio de IA no disponible")
    except Exception as e:
        logger.error(f"Error enviando a IA: {e}")
