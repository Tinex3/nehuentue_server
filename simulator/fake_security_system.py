#!/usr/bin/env python3
"""
Simulador de Sistema de Seguridad IoT
=====================================
Simula un sistema completo con:
- Sensor PIR (detección de movimiento)
- Relé (luz/alarma)
- Cámara (captura de imágenes)

Flujo:
1. PIR detecta movimiento
2. Se activa el Relé (luz)
3. Cámara captura imagen
4. Se envía todo por MQTT
"""

import paho.mqtt.client as mqtt
import json
import time
import random
import base64
import io
import os
import argparse
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import requests

# Configuración por defecto
DEFAULT_CONFIG = {
    "mqtt_host": "server.local",
    "mqtt_port": 1883,
    "mqtt_user": "device",
    "mqtt_password": "device123",
    "api_url": "http://server.local:5000/api",
    "device_id": 1,
    "zone_id": 1,
    "interval": 10,  # segundos entre eventos
}


class FakeSecuritySystem:
    def __init__(self, config: dict):
        self.config = config
        self.client = None
        self.connected = False
        self.relay_state = False
        self.event_count = 0
        
        # Carpeta de imágenes personalizadas
        self.images_dir = os.path.join(os.path.dirname(__file__), "images")
        self.custom_images = self._load_custom_images()
        self.image_index = 0
        
        # Topics MQTT - Alineados con el worker
        self.topics = {
            "pir": "events/motion",
            "relay": f"devices/{config['device_id']}/status",
            "camera": f"cameras/{config['device_id']}/frame",
            "telemetry": f"devices/{config['device_id']}/telemetry",
            "status": f"devices/{config['device_id']}/status",
        }
    
    def _load_custom_images(self) -> list:
        """Cargar imágenes personalizadas de la carpeta images/"""
        images = []
        if os.path.exists(self.images_dir):
            for filename in sorted(os.listdir(self.images_dir)):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                    filepath = os.path.join(self.images_dir, filename)
                    images.append(filepath)
            if images:
                print(f"📁 Cargadas {len(images)} imágenes personalizadas de {self.images_dir}")
            else:
                print(f"📁 No hay imágenes en {self.images_dir}, usando imágenes generadas")
        return images
    
    def _get_next_custom_image(self) -> bytes:
        """Obtener la siguiente imagen personalizada (rotación circular)"""
        if not self.custom_images:
            return None
        
        filepath = self.custom_images[self.image_index]
        self.image_index = (self.image_index + 1) % len(self.custom_images)
        
        try:
            # Abrir y redimensionar imagen si es necesario
            with Image.open(filepath) as img:
                # Convertir a RGB si es necesario
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Redimensionar si es muy grande (max 1280x960)
                max_size = (1280, 960)
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Agregar overlay con timestamp
                draw = ImageDraw.Draw(img)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
                except:
                    font = ImageFont.load_default()
                
                # Barra de información semi-transparente
                width, height = img.size
                draw.rectangle([0, 0, width, 30], fill=(0, 0, 0))
                draw.text((10, 5), f"CAM-{self.config['device_id']} | {timestamp} | {os.path.basename(filepath)}", 
                          fill=(255, 255, 255), font=font)
                
                # Convertir a JPEG bytes
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                print(f"📷 Usando imagen: {os.path.basename(filepath)}")
                return buffer.getvalue()
                
        except Exception as e:
            print(f"⚠️ Error cargando {filepath}: {e}")
            return None
        
    def connect_mqtt(self):
        """Conectar al broker MQTT"""
        self.client = mqtt.Client(client_id=f"fake_security_{self.config['device_id']}")
        self.client.username_pw_set(
            self.config["mqtt_user"], 
            self.config["mqtt_password"]
        )
        
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        print(f"🔌 Conectando a MQTT {self.config['mqtt_host']}:{self.config['mqtt_port']}...")
        
        try:
            self.client.connect(
                self.config["mqtt_host"],
                self.config["mqtt_port"],
                keepalive=60
            )
            self.client.loop_start()
            
            # Esperar conexión
            timeout = 10
            while not self.connected and timeout > 0:
                time.sleep(0.5)
                timeout -= 0.5
                
            if not self.connected:
                raise Exception("Timeout de conexión MQTT")
                
            # Suscribirse a comandos
            self.client.subscribe(f"iot/device/{self.config['device_id']}/command")
            print("✅ Conectado a MQTT")
            return True
            
        except Exception as e:
            print(f"❌ Error conectando a MQTT: {e}")
            return False
    
    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            print("📡 Conexión MQTT establecida")
        else:
            print(f"❌ Error de conexión MQTT: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        self.connected = False
        print("🔌 Desconectado de MQTT")
    
    def _on_message(self, client, userdata, msg):
        """Recibir comandos del servidor"""
        try:
            payload = json.loads(msg.payload.decode())
            print(f"📨 Comando recibido: {payload}")
            
            if payload.get("command") == "relay_on":
                self.relay_state = True
                print("💡 Relé encendido por comando remoto")
            elif payload.get("command") == "relay_off":
                self.relay_state = False
                print("🌑 Relé apagado por comando remoto")
                
        except Exception as e:
            print(f"Error procesando mensaje: {e}")
    
    def generate_fake_image(self, with_person: bool = True) -> bytes:
        """Generar una imagen falsa simulando una cámara de seguridad"""
        # Crear imagen 640x480
        width, height = 640, 480
        
        # Fondo (simular escena nocturna o diurna)
        is_night = random.random() > 0.5
        if is_night:
            bg_color = (20, 25, 35)  # Azul oscuro nocturno
        else:
            bg_color = (135, 180, 220)  # Cielo diurno
        
        img = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        
        # Dibujar suelo/piso
        floor_color = (80, 80, 80) if is_night else (120, 100, 80)
        draw.rectangle([0, height//2, width, height], fill=floor_color)
        
        # Dibujar una puerta o pared
        wall_color = (60, 50, 45) if is_night else (180, 160, 140)
        draw.rectangle([50, 100, 200, height//2 + 50], fill=wall_color)
        
        # Si hay persona, dibujar una silueta
        if with_person:
            person_x = random.randint(250, 500)
            person_y = height//2 - 20
            
            # Cabeza
            head_color = (200, 180, 160)
            draw.ellipse([person_x-15, person_y-80, person_x+15, person_y-50], fill=head_color)
            
            # Cuerpo
            body_color = random.choice([(50, 50, 150), (150, 50, 50), (50, 150, 50), (100, 100, 100)])
            draw.rectangle([person_x-20, person_y-50, person_x+20, person_y+60], fill=body_color)
            
            # Piernas
            draw.rectangle([person_x-18, person_y+60, person_x-5, person_y+120], fill=(40, 40, 80))
            draw.rectangle([person_x+5, person_y+60, person_x+18, person_y+120], fill=(40, 40, 80))
        
        # Agregar timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Usar fuente por defecto
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        # Barra de información
        draw.rectangle([0, 0, width, 30], fill=(0, 0, 0, 180))
        draw.text((10, 5), f"CAM-{self.config['device_id']} | Zone {self.config['zone_id']} | {timestamp}", 
                  fill=(255, 255, 255), font=font)
        
        # Indicador de movimiento si hay persona
        if with_person:
            draw.rectangle([width-120, 5, width-10, 25], fill=(255, 0, 0))
            draw.text((width-115, 5), "MOTION", fill=(255, 255, 255), font=font)
        
        # Agregar ruido para simular cámara real
        # (opcional, puede hacer la imagen más pesada)
        
        # Convertir a bytes JPEG
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        return buffer.getvalue()
    
    def send_pir_event(self) -> bool:
        """Enviar evento de detección PIR
        
        El worker espera:
        {
            "device_id": 1,
            "timestamp": "2024-01-01T12:00:00",
            "confidence": 0.95
        }
        """
        confidence = round(random.uniform(0.7, 1.0), 2)
        payload = {
            "device_id": self.config["device_id"],
            "timestamp": datetime.now().isoformat(),
            "confidence": confidence,
        }
        
        result = self.client.publish(
            self.topics["pir"],
            json.dumps(payload),
            qos=1
        )
        
        if result.rc == 0:
            print(f"🚶 PIR: Movimiento detectado (confianza: {confidence*100:.0f}%)")
            return True
        return False
    
    def send_relay_event(self, state: bool) -> bool:
        """Enviar evento de cambio de relé
        
        El worker espera:
        {
            "status": "online" | "offline" | "error",
            "timestamp": "...",
            "info": { ... }
        }
        """
        self.relay_state = state
        
        payload = {
            "status": "online" if state else "offline",
            "timestamp": datetime.now().isoformat(),
            "info": {
                "relay_state": state,
                "relay_id": 1,
                "zone_id": self.config["zone_id"],
            }
        }
        
        result = self.client.publish(
            self.topics["relay"],
            json.dumps(payload),
            qos=1
        )
        
        if result.rc == 0:
            icon = "💡" if state else "🌑"
            print(f"{icon} RELAY: {'Encendido' if state else 'Apagado'}")
            return True
        return False
    
    def send_camera_capture(self, with_person: bool = True) -> bool:
        """Capturar y enviar imagen de la cámara
        
        El worker espera:
        {
            "event_id": 123,        // opcional
            "zone_id": 1,           // opcional
            "timestamp": "...",
            "frame": "base64...",   // imagen en base64
            "format": "jpeg"
        }
        """
        print("📸 CAMERA: Capturando imagen...")
        
        # Usar imagen personalizada si existe, sino generar una falsa
        image_bytes = self._get_next_custom_image()
        if image_bytes is None:
            image_bytes = self.generate_fake_image(with_person)
        
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        payload = {
            "zone_id": self.config["zone_id"],
            "timestamp": datetime.now().isoformat(),
            "frame": image_base64,
            "format": "jpeg",
        }
        
        result = self.client.publish(
            self.topics["camera"],
            json.dumps(payload),
            qos=1
        )
        
        if result.rc == 0:
            size_kb = len(image_bytes) / 1024
            print(f"📷 CAMERA: Imagen enviada ({size_kb:.1f} KB, persona: {'Sí' if with_person else 'No'})")
            return True
        return False
    
    def send_telemetry(self) -> bool:
        """Enviar datos de telemetría (temperatura, humedad, etc.)
        
        El worker espera datos planos (no nested):
        {
            "timestamp": "2024-01-01T12:00:00",
            "temperature": 25.5,
            "humidity": 60,
            ...
        }
        """
        payload = {
            "timestamp": datetime.now().isoformat(),
            "temperature": round(random.uniform(18, 28), 1),
            "humidity": round(random.uniform(40, 70), 1),
            "battery": random.randint(70, 100),
            "wifi_signal": random.randint(-70, -30),
        }
        
        result = self.client.publish(
            self.topics["telemetry"],
            json.dumps(payload),
            qos=0
        )
        
        if result.rc == 0:
            print(f"📊 TELEMETRY: T={payload['temperature']}°C, H={payload['humidity']}%")
            return True
        return False
    
    def send_status(self) -> bool:
        """Enviar estado del dispositivo
        
        El worker espera:
        {
            "status": "online" | "offline" | "error",
            "timestamp": "...",
            "info": { ... }
        }
        """
        payload = {
            "status": "online",
            "timestamp": datetime.now().isoformat(),
            "info": {
                "relay_state": self.relay_state,
                "device_id": self.config["device_id"],
            }
        }
        
        result = self.client.publish(
            self.topics["status"],
            json.dumps(payload),
            qos=1
        )
        return result.rc == 0
    
    def run_security_sequence(self):
        """Ejecutar secuencia completa de seguridad"""
        self.event_count += 1
        print(f"\n{'='*50}")
        print(f"🔔 EVENTO DE SEGURIDAD #{self.event_count}")
        print(f"{'='*50}")
        
        # 1. PIR detecta movimiento
        time.sleep(0.5)
        self.send_pir_event()
        
        # 2. Encender relé (luz)
        time.sleep(1)
        self.send_relay_event(True)
        
        # 3. Capturar imagen (80% probabilidad de tener persona)
        time.sleep(0.5)
        has_person = random.random() < 0.8
        self.send_camera_capture(with_person=has_person)
        
        # 4. Enviar telemetría
        time.sleep(0.5)
        self.send_telemetry()
        
        # 5. Después de un tiempo, apagar relé
        time.sleep(3)
        self.send_relay_event(False)
        
        # 6. Enviar estado
        self.send_status()
        
        print(f"{'='*50}\n")
    
    def run(self):
        """Ejecutar el simulador"""
        if not self.connect_mqtt():
            return
        
        print(f"\n🚀 Simulador iniciado")
        print(f"   Device ID: {self.config['device_id']}")
        print(f"   Zone ID: {self.config['zone_id']}")
        print(f"   Intervalo: {self.config['interval']}s")
        print(f"\nPresiona Ctrl+C para detener\n")
        
        # Enviar estado inicial
        self.send_status()
        
        try:
            while True:
                self.run_security_sequence()
                
                # Esperar antes del próximo evento
                print(f"⏳ Próximo evento en {self.config['interval']} segundos...")
                time.sleep(self.config['interval'])
                
        except KeyboardInterrupt:
            print("\n\n🛑 Deteniendo simulador...")
            self.send_relay_event(False)
            self.client.loop_stop()
            self.client.disconnect()
            print("👋 Simulador detenido")


def main():
    parser = argparse.ArgumentParser(
        description="Simulador de Sistema de Seguridad IoT",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python fake_security_system.py
  python fake_security_system.py --host 192.168.1.100 --interval 5
  python fake_security_system.py --device-id 2 --zone-id 1
        """
    )
    
    parser.add_argument("--host", default=DEFAULT_CONFIG["mqtt_host"],
                        help=f"Host del broker MQTT (default: {DEFAULT_CONFIG['mqtt_host']})")
    parser.add_argument("--port", type=int, default=DEFAULT_CONFIG["mqtt_port"],
                        help=f"Puerto MQTT (default: {DEFAULT_CONFIG['mqtt_port']})")
    parser.add_argument("--user", default=DEFAULT_CONFIG["mqtt_user"],
                        help=f"Usuario MQTT (default: {DEFAULT_CONFIG['mqtt_user']})")
    parser.add_argument("--password", default=DEFAULT_CONFIG["mqtt_password"],
                        help="Contraseña MQTT")
    parser.add_argument("--device-id", type=int, default=DEFAULT_CONFIG["device_id"],
                        help=f"ID del dispositivo (default: {DEFAULT_CONFIG['device_id']})")
    parser.add_argument("--zone-id", type=int, default=DEFAULT_CONFIG["zone_id"],
                        help=f"ID de la zona (default: {DEFAULT_CONFIG['zone_id']})")
    parser.add_argument("--interval", type=int, default=DEFAULT_CONFIG["interval"],
                        help=f"Intervalo entre eventos en segundos (default: {DEFAULT_CONFIG['interval']})")
    
    args = parser.parse_args()
    
    config = {
        "mqtt_host": args.host,
        "mqtt_port": args.port,
        "mqtt_user": args.user,
        "mqtt_password": args.password,
        "device_id": args.device_id,
        "zone_id": args.zone_id,
        "interval": args.interval,
    }
    
    system = FakeSecuritySystem(config)
    system.run()


if __name__ == "__main__":
    main()
