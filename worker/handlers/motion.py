"""
Handler de eventos de movimiento (PIR)
Implementa RF1, RF2, RF3, RF4
"""
import json
import logging
from datetime import datetime, timedelta

from config import config

logger = logging.getLogger('worker.handlers.motion')


def handle_motion_event(db, mqtt_client, data: dict):
    """
    Procesa evento de movimiento detectado por sensor PIR
    
    Flujo:
    1. Valida el evento y obtiene información del dispositivo
    2. Verifica cooldown (evita eventos duplicados)
    3. Registra evento en base de datos
    4. Activa relés de iluminación de la zona
    5. Envía comando de captura a cámaras de la zona
    
    Payload esperado:
    {
        "device_id": 1,
        "timestamp": "2024-01-01T12:00:00",
        "confidence": 0.95  // opcional
    }
    """
    try:
        device_id = data.get('device_id')
        timestamp = data.get('timestamp', datetime.utcnow().isoformat())
        
        if not device_id:
            logger.warning("Evento de movimiento sin device_id")
            return
        
        logger.info(f"[MOTION] Evento de movimiento - Dispositivo: {device_id}")
        
        # Obtener información del dispositivo
        device = db.get_device_by_id(device_id)
        if not device:
            logger.warning(f"Dispositivo {device_id} no encontrado")
            return
        
        zone_id = device.get('zone_id')
        if not zone_id:
            logger.warning(f"Dispositivo {device_id} no tiene zona asignada")
            return
        
        # Verificar cooldown
        if not _check_cooldown(db, zone_id):
            logger.debug(f"Zona {zone_id} en cooldown, ignorando evento")
            return
        
        # Crear evento en base de datos
        event_id = db.create_event(
            device_id=device_id,
            zone_id=zone_id,
            event_type='motion',
            payload=data
        )
        
        logger.info(f"[MOTION] Evento registrado (ID: {event_id}) en zona {zone_id}")
        
        # Activar relés de la zona (RF3)
        _activate_zone_relays(db, mqtt_client, zone_id)
        
        # Comandar captura a cámaras de la zona (RF4)
        _trigger_zone_cameras(db, mqtt_client, zone_id, event_id)
        
    except Exception as e:
        logger.error(f"Error procesando evento de movimiento: {e}", exc_info=True)


def _check_cooldown(db, zone_id: int) -> bool:
    """
    Verifica si la zona está en período de cooldown
    Retorna True si se puede procesar el evento
    """
    last_event = db.get_last_motion_event(zone_id)
    
    if not last_event:
        return True
    
    last_time = last_event.get('created_at')
    if not last_time:
        return True
    
    # Calcular diferencia
    if isinstance(last_time, str):
        last_time = datetime.fromisoformat(last_time)
    
    cooldown = timedelta(seconds=config.MOTION_COOLDOWN_SECONDS)
    
    return datetime.utcnow() - last_time > cooldown


def _activate_zone_relays(db, mqtt_client, zone_id: int):
    """
    Activa todos los relés de iluminación en la zona (RF3)
    """
    relays = db.get_devices_by_zone(zone_id, device_type='relay')
    
    if not relays:
        logger.debug(f"No hay relés en zona {zone_id}")
        return
    
    for relay in relays:
        relay_id = relay['device_id']
        topic = f"commands/relays/{relay_id}"
        
        command = {
            'command': 'set',
            'state': 'on',
            'duration': config.AUTO_LIGHTS_DURATION,
            'reason': 'motion_detected',
            'zone_id': zone_id
        }
        
        mqtt_client.publish(topic, command)
        logger.info(f"[RELAY] Comando ON enviado a relé {relay_id}")
        
        # Registrar evento de relay
        db.create_event(
            device_id=relay_id,
            zone_id=zone_id,
            event_type='relay_on',
            payload={'trigger': 'motion', 'duration': config.AUTO_LIGHTS_DURATION}
        )


def _trigger_zone_cameras(db, mqtt_client, zone_id: int, event_id: int):
    """
    Envía comando de captura a todas las cámaras de la zona (RF4)
    """
    cameras = db.get_devices_by_zone(zone_id, device_type='camera')
    
    if not cameras:
        logger.debug(f"No hay cámaras en zona {zone_id}")
        return
    
    for camera in cameras:
        camera_id = camera['device_id']
        topic = f"commands/cameras/{camera_id}"
        
        command = {
            'command': 'capture',
            'frames': config.CAPTURE_FRAMES_ON_MOTION,
            'event_id': event_id,
            'zone_id': zone_id,
            'reason': 'motion_detected'
        }
        
        mqtt_client.publish(topic, command)
        logger.info(f"[CAMERA] Comando de captura enviado a cámara {camera_id}")
