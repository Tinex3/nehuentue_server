"""
Manejador MQTT - Suscripción y procesamiento de mensajes
"""
import json
import logging
import paho.mqtt.client as mqtt
from typing import Callable
from threading import Thread

from config import config
from handlers import (
    handle_motion_event,
    handle_device_status,
    handle_telemetry,
    handle_camera_frame
)

logger = logging.getLogger('worker.mqtt')


class MQTTHandler:
    """Manejador de conexión y mensajes MQTT"""
    
    def __init__(self, db):
        self.db = db
        self.client = mqtt.Client(
            client_id=config.MQTT_CLIENT_ID,
            clean_session=True
        )
        self.client.username_pw_set(config.MQTT_USER, config.MQTT_PASSWORD)
        
        # Callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        self.connected = False
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback cuando se conecta al broker"""
        if rc == 0:
            self.connected = True
            logger.info(f"Conectado al broker MQTT {config.MQTT_BROKER}:{config.MQTT_PORT}")
            
            # Suscribirse a tópicos
            for topic, qos in config.MQTT_TOPICS:
                client.subscribe(topic, qos)
                logger.info(f"Suscrito a: {topic}")
        else:
            logger.error(f"Error de conexión MQTT, código: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback cuando se desconecta"""
        self.connected = False
        if rc != 0:
            logger.warning(f"Desconexión inesperada del broker MQTT, código: {rc}")
        else:
            logger.info("Desconectado del broker MQTT")
    
    def _on_message(self, client, userdata, msg):
        """Callback cuando llega un mensaje"""
        try:
            topic = msg.topic
            payload = msg.payload
            
            logger.debug(f"Mensaje recibido en {topic}: {payload[:100]}")
            
            # Parsear payload JSON si es posible
            try:
                data = json.loads(payload.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Puede ser binario (imagen)
                data = payload
            
            # Rutear mensaje al handler apropiado
            self._route_message(topic, data, payload)
            
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}", exc_info=True)
    
    def _route_message(self, topic: str, data, raw_payload: bytes):
        """Rutea el mensaje al handler correcto según el tópico"""
        
        # events/motion
        if topic == 'events/motion':
            handle_motion_event(self.db, self.client, data)
        
        # devices/{device_id}/status
        elif topic.startswith('devices/') and topic.endswith('/status'):
            parts = topic.split('/')
            if len(parts) == 3:
                device_id = parts[1]
                handle_device_status(self.db, device_id, data)
        
        # devices/{device_id}/telemetry
        elif topic.startswith('devices/') and topic.endswith('/telemetry'):
            parts = topic.split('/')
            if len(parts) == 3:
                device_id = parts[1]
                handle_telemetry(self.db, device_id, data)
        
        # cameras/{camera_id}/frame
        elif topic.startswith('cameras/') and topic.endswith('/frame'):
            parts = topic.split('/')
            if len(parts) == 3:
                camera_id = parts[1]
                handle_camera_frame(self.db, camera_id, data, raw_payload)
        
        else:
            logger.debug(f"Tópico no manejado: {topic}")
    
    def publish(self, topic: str, payload: dict, qos: int = 1, retain: bool = False):
        """Publicar mensaje en un tópico"""
        message = json.dumps(payload)
        result = self.client.publish(topic, message, qos=qos, retain=retain)
        
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            logger.error(f"Error al publicar en {topic}: {result.rc}")
        else:
            logger.debug(f"Publicado en {topic}: {message[:100]}")
        
        return result
    
    def start(self):
        """Iniciar conexión y loop MQTT"""
        try:
            self.client.connect(config.MQTT_BROKER, config.MQTT_PORT, keepalive=60)
            self.client.loop_start()
            logger.info("Loop MQTT iniciado")
        except Exception as e:
            logger.error(f"Error al iniciar MQTT: {e}")
            raise
    
    def stop(self):
        """Detener conexión MQTT"""
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("Conexión MQTT cerrada")
