"""
Cliente MQTT para envío de comandos
"""
import json
import os
import paho.mqtt.client as mqtt
from threading import Lock

# Configuración MQTT
MQTT_BROKER = os.environ.get('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.environ.get('MQTT_PORT', 1883))
MQTT_USER = os.environ.get('MQTT_USER', 'backend')
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD', 'backend123')

# Cliente singleton
_client = None
_lock = Lock()


class MQTTClient:
    """Cliente MQTT singleton para el backend"""
    
    def __init__(self):
        self.client = mqtt.Client(client_id="iot-backend", clean_session=True)
        self.client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.connected = False
    
    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            print(f"[MQTT] Conectado al broker {MQTT_BROKER}:{MQTT_PORT}")
        else:
            print(f"[MQTT] Error de conexión, código: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        self.connected = False
        print(f"[MQTT] Desconectado del broker, código: {rc}")
    
    def connect(self):
        """Conectar al broker MQTT"""
        try:
            self.client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
            self.client.loop_start()
        except Exception as e:
            print(f"[MQTT] Error al conectar: {e}")
            raise
    
    def disconnect(self):
        """Desconectar del broker"""
        self.client.loop_stop()
        self.client.disconnect()
    
    def publish(self, topic: str, payload: dict, qos: int = 1, retain: bool = False):
        """Publicar mensaje en un tópico"""
        if not self.connected:
            self.connect()
        
        message = json.dumps(payload)
        result = self.client.publish(topic, message, qos=qos, retain=retain)
        
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            raise Exception(f"Error al publicar mensaje: {result.rc}")
        
        return result


def get_mqtt_client() -> MQTTClient:
    """Obtener instancia singleton del cliente MQTT"""
    global _client
    
    with _lock:
        if _client is None:
            _client = MQTTClient()
            _client.connect()
        return _client


def publish_command(topic: str, payload: dict, qos: int = 1):
    """Función de conveniencia para publicar comandos"""
    client = get_mqtt_client()
    return client.publish(topic, payload, qos=qos)
