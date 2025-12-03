#!/usr/bin/env python3
"""
Simulador IoT - CLI Principal
Simula sensores PIR, cámaras y sensores de temperatura desde tu PC
"""
import os
import sys
import time
import random
import argparse
from pathlib import Path
from datetime import datetime

# Agregar path para imports locales
sys.path.insert(0, str(Path(__file__).parent))

from mqtt_simulator import MQTTSimulator, ImageFolderSimulator, create_sample_images_folder
from api_client import AIServiceClient, BackendAPIClient, print_detection_results

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

console = Console() if RICH_AVAILABLE else None


def print_header():
    """Mostrar header del simulador"""
    header = """
╔═══════════════════════════════════════════════════════════════╗
║           🔐 SIMULADOR IoT - Sistema de Seguridad             ║
║                                                               ║
║  Simula dispositivos IoT desde tu PC para pruebas            ║
║  • Sensores PIR (movimiento)                                  ║
║  • Cámaras (envío de imágenes)                               ║
║  • Sensores de temperatura/humedad                           ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(header)


def cmd_mqtt_test(args):
    """Probar conexión MQTT"""
    print("\n🔗 Probando conexión MQTT...")
    
    sim = MQTTSimulator()
    
    if sim.connect():
        print("✅ Conexión exitosa!")
        print(f"   Broker: {sim.broker}:{sim.port}")
        print(f"   Usuario: {sim.username}")
        print(f"   Device ID: {sim.device_id}")
        
        # Enviar status de prueba
        sim.send_device_status("active")
        time.sleep(1)
        
        sim.disconnect()
    else:
        print("❌ No se pudo conectar al broker MQTT")
        print("   Verifica que el broker esté corriendo")


def cmd_send_motion(args):
    """Enviar evento de movimiento"""
    print("\n🚶 Enviando evento de movimiento...")
    
    sim = MQTTSimulator()
    
    if not sim.connect():
        print("❌ No se pudo conectar")
        return
    
    count = args.count or 1
    interval = args.interval or 5
    
    for i in range(count):
        confidence = random.uniform(0.7, 1.0)
        sim.send_motion_event(confidence)
        
        if i < count - 1:
            print(f"   Esperando {interval}s...")
            time.sleep(interval)
    
    sim.disconnect()
    print(f"\n✅ Enviados {count} eventos de movimiento")


def cmd_send_telemetry(args):
    """Enviar datos de telemetría"""
    print("\n📊 Enviando telemetría...")
    
    sim = MQTTSimulator()
    
    if not sim.connect():
        print("❌ No se pudo conectar")
        return
    
    count = args.count or 1
    interval = args.interval or 10
    
    for i in range(count):
        temp = args.temperature or random.uniform(18, 30)
        hum = args.humidity or random.uniform(40, 80)
        
        sim.send_telemetry(temperature=temp, humidity=hum)
        
        if i < count - 1:
            print(f"   Esperando {interval}s...")
            time.sleep(interval)
    
    sim.disconnect()
    print(f"\n✅ Enviadas {count} lecturas de telemetría")


def cmd_send_image(args):
    """Enviar imagen(es)"""
    image_path = args.image
    folder_path = args.folder
    
    sim = MQTTSimulator()
    
    if not sim.connect():
        print("❌ No se pudo conectar al broker MQTT")
        return
    
    if image_path:
        # Enviar imagen específica
        if not Path(image_path).exists():
            print(f"❌ Imagen no encontrada: {image_path}")
            return
        
        print(f"\n📸 Enviando imagen: {image_path}")
        
        if args.with_motion:
            sim.send_motion_event()
            time.sleep(0.5)
        
        sim.send_camera_frame(image_path)
        
    elif folder_path:
        # Enviar todas las imágenes de una carpeta
        folder_sim = ImageFolderSimulator(sim, folder_path)
        
        images = folder_sim.get_images()
        if not images:
            print(f"❌ No se encontraron imágenes en: {folder_path}")
            return
        
        print(f"\n📁 Encontradas {len(images)} imágenes en {folder_path}")
        
        interval = args.interval or 2
        folder_sim.send_all_images(interval=interval, with_motion=args.with_motion)
    
    else:
        print("❌ Especifica --image o --folder")
        return
    
    sim.disconnect()


def cmd_ai_detect(args):
    """Detectar objetos en imagen usando API de IA"""
    image_path = args.image
    folder_path = args.folder
    
    if not image_path and not folder_path:
        print("❌ Especifica --image o --folder")
        return
    
    ai_client = AIServiceClient()
    
    # Verificar servicio
    print("\n🔍 Verificando servicio de IA...")
    health = ai_client.health_check()
    
    if health.get("status") != "ok":
        print(f"⚠️  Servicio de IA no disponible: {health.get('message', 'Error desconocido')}")
        print("   Asegúrate de que el servicio esté corriendo en http://localhost:5001")
        return
    
    print("✅ Servicio de IA disponible")
    
    # Procesar imagen(es)
    if image_path:
        images = [Path(image_path)]
    else:
        folder = Path(folder_path)
        images = list(folder.glob("*.jpg")) + list(folder.glob("*.jpeg")) + list(folder.glob("*.png"))
    
    if not images:
        print("❌ No se encontraron imágenes")
        return
    
    print(f"\n📷 Procesando {len(images)} imagen(es)...\n")
    
    for img_path in images:
        if not img_path.exists():
            print(f"❌ No existe: {img_path}")
            continue
        
        print(f"🔍 Analizando: {img_path.name}")
        results = ai_client.detect_objects(str(img_path))
        print_detection_results(results, img_path.name)
        
        if len(images) > 1:
            time.sleep(0.5)


def cmd_continuous(args):
    """Modo continuo - simula sensor activo"""
    print("\n🔄 Iniciando modo continuo...")
    print("   Presiona Ctrl+C para detener\n")
    
    sim = MQTTSimulator()
    
    if not sim.connect():
        print("❌ No se pudo conectar")
        return
    
    # Parámetros
    telemetry_interval = args.telemetry_interval or 30
    motion_probability = args.motion_probability or 0.1
    images_folder = args.images_folder
    
    folder_sim = None
    if images_folder and Path(images_folder).exists():
        folder_sim = ImageFolderSimulator(sim, images_folder)
        print(f"📁 Carpeta de imágenes: {images_folder}")
    
    print(f"⏱️  Intervalo telemetría: {telemetry_interval}s")
    print(f"🎲 Probabilidad movimiento: {motion_probability*100:.0f}%")
    print("\n" + "="*50)
    
    # Enviar status inicial
    sim.send_device_status("active")
    
    iteration = 0
    try:
        while True:
            iteration += 1
            print(f"\n[Iteración {iteration}] {datetime.now().strftime('%H:%M:%S')}")
            
            # Siempre enviar telemetría
            sim.send_telemetry()
            
            # Posibilidad de movimiento
            if random.random() < motion_probability:
                print("🚶 ¡Movimiento detectado!")
                sim.send_motion_event()
                
                # Si hay carpeta de imágenes, enviar una
                if folder_sim:
                    time.sleep(0.5)
                    folder_sim.send_random_image(with_motion=False)
            
            time.sleep(telemetry_interval)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Detenido por usuario")
    
    sim.send_device_status("inactive")
    sim.disconnect()


def cmd_setup(args):
    """Configuración inicial"""
    print("\n⚙️  Configuración del simulador\n")
    
    # Crear carpeta de imágenes
    images_folder = create_sample_images_folder()
    
    # Crear .env si no existe
    env_path = Path(".env")
    if not env_path.exists():
        env_example = Path(".env.example")
        if env_example.exists():
            import shutil
            shutil.copy(env_example, env_path)
            print(f"✅ Creado archivo .env desde .env.example")
        else:
            print("⚠️  No se encontró .env.example")
    else:
        print(f"✅ Archivo .env ya existe")
    
    print("\n📋 Próximos pasos:")
    print("   1. Edita el archivo .env con tu configuración")
    print(f"   2. Coloca imágenes en: {images_folder.absolute()}")
    print("   3. Ejecuta: python main.py test-mqtt")
    print("   4. Ejecuta: python main.py send-image --folder ./images")


def cmd_status(args):
    """Ver estado del sistema"""
    print("\n📊 Estado del Sistema\n")
    
    # Verificar servicios
    services = [
        ("MQTT Broker", os.getenv('MQTT_BROKER', 'localhost'), os.getenv('MQTT_PORT', '1883')),
        ("Backend API", os.getenv('API_URL', 'http://localhost:5000/api'), None),
        ("AI Service", os.getenv('AI_SERVICE_URL', 'http://localhost:5001'), None),
    ]
    
    print("Servicios configurados:")
    for name, host, port in services:
        url = f"{host}:{port}" if port else host
        print(f"  • {name}: {url}")
    
    print("\n🔍 Verificando conectividad...\n")
    
    # Probar AI Service
    ai_client = AIServiceClient()
    health = ai_client.health_check()
    status = "✅ Online" if health.get("status") == "ok" else "❌ Offline"
    print(f"  AI Service: {status}")
    
    # Probar Backend
    backend_client = BackendAPIClient()
    try:
        import requests
        resp = requests.get(f"{backend_client.base_url.replace('/api', '')}/health", timeout=5)
        status = "✅ Online" if resp.status_code == 200 else "❌ Error"
    except:
        status = "❌ Offline"
    print(f"  Backend API: {status}")
    
    # Probar MQTT
    print(f"  MQTT Broker: (usa 'test-mqtt' para verificar)")


def main():
    """Punto de entrada principal"""
    print_header()
    
    parser = argparse.ArgumentParser(
        description="Simulador de dispositivos IoT",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # Comando: setup
    setup_parser = subparsers.add_parser('setup', help='Configuración inicial')
    setup_parser.set_defaults(func=cmd_setup)
    
    # Comando: status
    status_parser = subparsers.add_parser('status', help='Ver estado del sistema')
    status_parser.set_defaults(func=cmd_status)
    
    # Comando: test-mqtt
    test_parser = subparsers.add_parser('test-mqtt', help='Probar conexión MQTT')
    test_parser.set_defaults(func=cmd_mqtt_test)
    
    # Comando: send-motion
    motion_parser = subparsers.add_parser('send-motion', help='Enviar evento de movimiento')
    motion_parser.add_argument('-c', '--count', type=int, default=1, help='Cantidad de eventos')
    motion_parser.add_argument('-i', '--interval', type=float, default=5, help='Intervalo entre eventos (seg)')
    motion_parser.set_defaults(func=cmd_send_motion)
    
    # Comando: send-telemetry
    tele_parser = subparsers.add_parser('send-telemetry', help='Enviar datos de telemetría')
    tele_parser.add_argument('-c', '--count', type=int, default=1, help='Cantidad de lecturas')
    tele_parser.add_argument('-i', '--interval', type=float, default=10, help='Intervalo entre lecturas (seg)')
    tele_parser.add_argument('-t', '--temperature', type=float, help='Temperatura fija')
    tele_parser.add_argument('-u', '--humidity', type=float, help='Humedad fija')
    tele_parser.set_defaults(func=cmd_send_telemetry)
    
    # Comando: send-image
    img_parser = subparsers.add_parser('send-image', help='Enviar imagen(es)')
    img_parser.add_argument('--image', '-f', help='Ruta a imagen específica')
    img_parser.add_argument('--folder', '-d', help='Carpeta con imágenes')
    img_parser.add_argument('--interval', '-i', type=float, default=2, help='Intervalo entre imágenes (seg)')
    img_parser.add_argument('--with-motion', '-m', action='store_true', default=True, help='Enviar evento de movimiento antes')
    img_parser.set_defaults(func=cmd_send_image)
    
    # Comando: ai-detect
    ai_parser = subparsers.add_parser('ai-detect', help='Detectar objetos con IA (sin MQTT)')
    ai_parser.add_argument('--image', '-f', help='Ruta a imagen específica')
    ai_parser.add_argument('--folder', '-d', help='Carpeta con imágenes')
    ai_parser.set_defaults(func=cmd_ai_detect)
    
    # Comando: continuous
    cont_parser = subparsers.add_parser('continuous', help='Modo continuo (simula sensor activo)')
    cont_parser.add_argument('--telemetry-interval', type=int, default=30, help='Intervalo telemetría (seg)')
    cont_parser.add_argument('--motion-probability', type=float, default=0.1, help='Probabilidad de movimiento (0-1)')
    cont_parser.add_argument('--images-folder', help='Carpeta de imágenes para capturas')
    cont_parser.set_defaults(func=cmd_continuous)
    
    # Parsear argumentos
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        print("\n📌 Ejemplos de uso:")
        print("   python main.py setup                    # Configuración inicial")
        print("   python main.py test-mqtt                # Probar conexión MQTT")
        print("   python main.py send-motion -c 5         # Enviar 5 eventos de movimiento")
        print("   python main.py send-image -f foto.jpg   # Enviar una imagen")
        print("   python main.py send-image -d ./images   # Enviar todas las imágenes")
        print("   python main.py ai-detect -f foto.jpg    # Detectar objetos en imagen")
        print("   python main.py continuous               # Modo sensor continuo")
        return
    
    # Ejecutar comando
    args.func(args)


if __name__ == "__main__":
    main()
