"""
Handler de telemetría
Implementa RF8 - Almacenamiento de mediciones en JSONB
"""
import logging
from datetime import datetime

logger = logging.getLogger('worker.handlers.telemetry')


def handle_telemetry(db, device_id: str, data: dict):
    """
    Procesa datos de telemetría de dispositivos
    
    Payload esperado:
    {
        "timestamp": "2024-01-01T12:00:00",  // o "recorded_at"
        "temperature": 25.5,
        "humidity": 60,
        "voltage": 3.3,
        ... // cualquier dato de telemetría
    }
    
    Todos los datos se almacenan en el campo JSONB 'data'
    """
    try:
        device_id_int = int(device_id)
        
        # Extraer timestamp
        recorded_at = data.pop('timestamp', None) or data.pop('recorded_at', None)
        if not recorded_at:
            recorded_at = datetime.utcnow().isoformat()
        
        # El resto de datos va al campo JSONB
        if not data:
            logger.debug(f"Telemetría vacía de dispositivo {device_id}")
            return
        
        # Crear medición
        measurement_id = db.create_measurement(
            device_id=device_id_int,
            recorded_at=recorded_at,
            data=data
        )
        
        logger.debug(f"[TELEMETRY] Medición {measurement_id} de dispositivo {device_id}: {data}")
        
    except ValueError:
        logger.warning(f"device_id inválido: {device_id}")
    except Exception as e:
        logger.error(f"Error procesando telemetría: {e}", exc_info=True)
