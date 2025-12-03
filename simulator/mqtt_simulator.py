"""
Simulador de Sensores IoT - Cliente MQTT
Simula dispositivos IoT enviando datos a través de MQTT
"""
import os
import json
import time
import random
import base64
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('iot-simulator')


class MQTTSimulator:
    """Cliente MQTT para simular dispositivos IoT"""
    
    def __init__(self):
        self.broker = os.getenv('MQTT_BROKER', 'localhost')
        self.port = int(os.getenv('MQTT_PORT', 1883))
        self.username = os.getenv('MQTT_USER', 'iot_system')
        self.password = os.getenv('MQTT_PASSWORD', 'iot_password_123')
        
        self.device_id = int(os.getenv('DEVICE_ID', 1))
        self.zone_id = int(os.getenv('ZONE_ID', 1))
        self.device_name = os.getenv('DEVICE_NAME', 'SimuladorPC')
        
        self.client = mqtt.Client(client_id=f"simulator_{self.device_id}_{int(time.time())}")
        self.client.username_pw_set(self.username, self.password)
        
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        self.connected = False
        
    def _on_connect(self, client, userdata, flags, rc):
        """Callback de conexión"""
        if rc == 0:
            logger.info(f"✅ Conectado al broker MQTT: {self.broker}:{self.port}")
            self.connected = True
            
            # Suscribirse a comandos
            command_topic = f"devices/{self.device_id}/command"
            client.subscribe(command_topic)
            logger.info(f"📥 Suscrito a: {command_topic}")
        else:
            logger.error(f"❌ Error de conexión, código: {rc}")
            self.connected = False
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback de desconexión"""
        logger.warning(f"🔌 Desconectado del broker (rc={rc})")
        self.connected = False
    
    def _on_message(self, client, userdata, msg):
        """Callback de mensajes recibidos"""
        try:
            payload = json.loads(msg.payload.decode())
            logger.info(f"📨 Comando recibido en {msg.topic}: {payload}")
            
            # Procesar comando
            command = payload.get('command', '')
            if command == 'on':
                logger.info("💡 Comando ON recibido - Simulando encendido")
            elif command == 'off':
                logger.info("🌑 Comando OFF recibido - Simulando apagado")
            elif command == 'capture':
                logger.info("📸 Comando CAPTURE recibido - Enviando imagen")
                # Aquí podría auto-enviarse una imagen
                
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}")
    
    def connect(self) -> bool:
        """Conectar al broker MQTT"""
        try:
            logger.info(f"🔗 Conectando a {self.broker}:{self.port}...")
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            
            # Esperar conexión
            timeout = 10
            while not self.connected and timeout > 0:
                time.sleep(0.5)
                timeout -= 0.5
            
            return self.connected
            
        except Exception as e:
            logger.error(f"❌ Error conectando: {e}")
            return False
    
    def disconnect(self):
        """Desconectar del broker"""
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("🔌 Desconectado")
    
    def publish(self, topic: str, payload: dict) -> bool:
        """Publicar mensaje"""
        try:
            message = json.dumps(payload)
            result = self.client.publish(topic, message, qos=1)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"📤 Publicado en {topic}")
                return True
            else:
                logger.error(f"❌ Error publicando: {result.rc}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return False
    
    # ==================== SIMULACIÓN DE SENSORES ====================
    
    def send_motion_event(self, confidence: float = None):
        """Simular evento de movimiento (PIR)"""
        if confidence is None:
            confidence = random.uniform(0.7, 1.0)
        
        payload = {
            "device_id": self.device_id,
            "zone_id": self.zone_id,
            "timestamp": datetime.utcnow().isoformat(),
            "confidence": round(confidence, 2),
            "sensor_type": "pir"
        }
        
        topic = "events/motion"
        logger.info(f"🚶 Enviando evento de movimiento (confianza: {confidence:.2f})")
        return self.publish(topic, payload)
    
    def send_telemetry(self, temperature: float = None, humidity: float = None, 
                       pressure: float = None):
        """Simular datos de telemetría (DHT22, BME280)"""
        if temperature is None:
            temperature = random.uniform(18.0, 30.0)
        if humidity is None:
            humidity = random.uniform(40.0, 80.0)
        if pressure is None:
            pressure = random.uniform(1000.0, 1025.0)
        
        payload = {
            "device_id": self.device_id,
            "timestamp": datetime.utcnow().isoformat(),
            "temperature": round(temperature, 1),
            "humidity": round(humidity, 1),
            "pressure": round(pressure, 1),
            "battery": random.randint(70, 100)
        }
        
        topic = f"devices/{self.device_id}/telemetry"
        logger.info(f"📊 Enviando telemetría: {temperature:.1f}°C, {humidity:.1f}%, {pressure:.1f}hPa")
        return self.publish(topic, payload)
    
    def send_device_status(self, status: str = "active"):
        """Enviar estado del dispositivo"""
        payload = {
            "device_id": self.device_id,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": random.randint(0, 86400),
            "rssi": random.randint(-80, -30),  # Señal WiFi
            "free_heap": random.randint(20000, 50000)
        }
        
        topic = f"devices/{self.device_id}/status"
        logger.info(f"📱 Enviando estado: {status}")
        return self.publish(topic, payload)
    
    def send_camera_frame(self, image_path: str, motion_detected: bool = True):
        """Enviar frame de cámara (imagen en base64)"""
        try:
            # Leer imagen
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Convertir a base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Obtener info de la imagen
            file_size = len(image_data)
            file_name = Path(image_path).name
            
            payload = {
                "device_id": self.device_id,
                "zone_id": self.zone_id,
                "timestamp": datetime.utcnow().isoformat(),
                "motion_detected": motion_detected,
                "image": image_base64,
                "format": Path(image_path).suffix.lower().replace('.', ''),
                "filename": file_name,
                "size": file_size
            }
            
            topic = f"cameras/{self.device_id}/frame"
            logger.info(f"📸 Enviando imagen: {file_name} ({file_size/1024:.1f} KB)")
            return self.publish(topic, payload)
            
        except FileNotFoundError:
            logger.error(f"❌ Imagen no encontrada: {image_path}")
            return False
        except Exception as e:
            logger.error(f"❌ Error enviando imagen: {e}")
            return False
    
    def send_relay_event(self, state: str = "on", reason: str = "manual"):
        """Simular evento de relay"""
        payload = {
            "device_id": self.device_id,
            "zone_id": self.zone_id,
            "timestamp": datetime.utcnow().isoformat(),
            "state": state,
            "reason": reason
        }
        
        event_type = "relay_on" if state == "on" else "relay_off"
        topic = f"events/{event_type}"
        logger.info(f"💡 Enviando evento relay: {state} ({reason})")
        return self.publish(topic, payload)


class ImageFolderSimulator:
    """Simulador que envía imágenes desde una carpeta"""
    
    def __init__(self, mqtt_sim: MQTTSimulator, images_folder: str):
        self.mqtt = mqtt_sim
        self.images_folder = Path(images_folder)
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
        
    def get_images(self) -> List[Path]:
        """Obtener lista de imágenes en la carpeta"""
        if not self.images_folder.exists():
            logger.warning(f"⚠️ Carpeta no existe: {self.images_folder}")
            return []
        
        images = []
        for ext in self.image_extensions:
            images.extend(self.images_folder.glob(f"*{ext}"))
            images.extend(self.images_folder.glob(f"*{ext.upper()}"))
        
        return sorted(images)
    
    def send_all_images(self, interval: float = 2.0, with_motion: bool = True):
        """Enviar todas las imágenes de la carpeta"""
        images = self.get_images()
        
        if not images:
            logger.warning("⚠️ No se encontraron imágenes")
            return
        
        logger.info(f"📁 Encontradas {len(images)} imágenes")
        
        for i, image_path in enumerate(images, 1):
            logger.info(f"\n{'='*50}")
            logger.info(f"📷 Imagen {i}/{len(images)}: {image_path.name}")
            
            if with_motion:
                # Primero enviar evento de movimiento
                self.mqtt.send_motion_event()
                time.sleep(0.5)
            
            # Enviar imagen
            self.mqtt.send_camera_frame(str(image_path))
            
            if i < len(images):
                logger.info(f"⏳ Esperando {interval}s...")
                time.sleep(interval)
        
        logger.info(f"\n✅ Enviadas {len(images)} imágenes")
    
    def send_random_image(self, with_motion: bool = True):
        """Enviar una imagen aleatoria"""
        images = self.get_images()
        
        if not images:
            logger.warning("⚠️ No se encontraron imágenes")
            return False
        
        image_path = random.choice(images)
        
        if with_motion:
            self.mqtt.send_motion_event()
            time.sleep(0.5)
        
        return self.mqtt.send_camera_frame(str(image_path))


def create_sample_images_folder():
    """Crear carpeta de imágenes de ejemplo"""
    images_folder = Path("./images")
    images_folder.mkdir(exist_ok=True)
    
    readme_path = images_folder / "README.txt"
    readme_path.write_text("""
Carpeta de Imágenes para Simulación
===================================

Coloca aquí las imágenes que quieres usar para simular capturas de cámara.

Formatos soportados: .jpg, .jpeg, .png, .gif, .bmp

Ejemplos de uso:
- Fotos de prueba con personas
- Imágenes de seguridad
- Screenshots de cámaras

Las imágenes serán enviadas al sistema como si fueran capturas de una cámara IoT.
""")
    
    logger.info(f"📁 Carpeta de imágenes creada: {images_folder.absolute()}")
    return images_folder
