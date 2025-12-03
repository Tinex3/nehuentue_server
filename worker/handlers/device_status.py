"""
Handler de estado de dispositivos
"""
import logging
from datetime import datetime

logger = logging.getLogger('worker.handlers.device_status')


def handle_device_status(db, device_id: str, data: dict):
    """
    Procesa actualizaciones de estado de dispositivos
    
    Payload esperado:
    {
        "status": "online" | "offline" | "error",
        "timestamp": "2024-01-01T12:00:00",
        "info": { ... }  // información adicional opcional
    }
    """
    try:
        device_id_int = int(device_id)
        status = data.get('status', 'unknown')
        
        logger.info(f"[STATUS] Dispositivo {device_id}: {status}")
        
        # Mapear estado a booleano
        is_active = status in ['online', 'active', 'ok']
        
        # Actualizar estado en BD
        db.update_device_status(device_id_int, is_active)
        
        # Si hay error, registrar evento
        if status == 'error':
            device = db.get_device_by_id(device_id_int)
            zone_id = device.get('zone_id') if device else None
            
            db.create_event(
                device_id=device_id_int,
                zone_id=zone_id,
                event_type='error',
                payload={
                    'error_status': status,
                    'info': data.get('info'),
                    'timestamp': data.get('timestamp', datetime.utcnow().isoformat())
                }
            )
            logger.warning(f"[STATUS] Error registrado para dispositivo {device_id}")
        
    except ValueError:
        logger.warning(f"device_id inválido: {device_id}")
    except Exception as e:
        logger.error(f"Error procesando estado de dispositivo: {e}", exc_info=True)
