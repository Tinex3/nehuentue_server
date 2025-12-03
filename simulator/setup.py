#!/usr/bin/env python3
"""
Script de configuración inicial del simulador
"""
import os
import sys
import shutil
from pathlib import Path

def main():
    print("=" * 60)
    print("  CONFIGURACIÓN DEL SIMULADOR IoT")
    print("=" * 60)
    print()
    
    base_dir = Path(__file__).parent
    
    # 1. Crear carpeta de imágenes
    images_dir = base_dir / "images"
    if not images_dir.exists():
        images_dir.mkdir()
        print(f"✅ Carpeta creada: {images_dir}")
        
        # Crear README
        readme = images_dir / "README.txt"
        readme.write_text("""
CARPETA DE IMÁGENES DE PRUEBA
=============================

Coloca aquí las imágenes que deseas usar para simular
capturas de cámara IoT.

Formatos soportados:
- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)

Las imágenes serán enviadas al sistema como si fueran
capturas reales de sensores.

Ejemplo de uso:
    python main.py
    > Seleccionar "Enviar imagen(es)"
    > Seleccionar "Carpeta completa"
""")
        print(f"✅ README creado en {readme}")
    else:
        print(f"ℹ️  Carpeta de imágenes ya existe: {images_dir}")
    
    # 2. Crear .env si no existe
    env_file = base_dir / ".env"
    env_example = base_dir / ".env.example"
    
    if not env_file.exists():
        if env_example.exists():
            shutil.copy(env_example, env_file)
            print(f"✅ Archivo .env creado desde .env.example")
        else:
            # Crear .env básico
            env_content = """# Configuración del Simulador IoT

# MQTT Broker
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_USER=device
MQTT_PASSWORD=device123

# API URLs
API_URL=http://localhost:5000/api
AI_SERVICE_URL=http://localhost:5001

# Dispositivo simulado
DEVICE_ID=1
ZONE_ID=1
DEVICE_NAME=SimuladorPC
"""
            env_file.write_text(env_content)
            print(f"✅ Archivo .env creado con valores por defecto")
    else:
        print(f"ℹ️  Archivo .env ya existe")
    
    # 3. Verificar dependencias
    print()
    print("Verificando dependencias...")
    
    missing_deps = []
    
    try:
        import paho.mqtt.client
        print("  ✅ paho-mqtt")
    except ImportError:
        print("  ❌ paho-mqtt")
        missing_deps.append("paho-mqtt")
    
    try:
        import requests
        print("  ✅ requests")
    except ImportError:
        print("  ❌ requests")
        missing_deps.append("requests")
    
    try:
        from PIL import Image
        print("  ✅ Pillow")
    except ImportError:
        print("  ❌ Pillow")
        missing_deps.append("Pillow")
    
    try:
        import dotenv
        print("  ✅ python-dotenv")
    except ImportError:
        print("  ❌ python-dotenv")
        missing_deps.append("python-dotenv")
    
    try:
        import click
        print("  ✅ click")
    except ImportError:
        print("  ❌ click")
        missing_deps.append("click")
    
    try:
        import rich
        print("  ✅ rich")
    except ImportError:
        print("  ❌ rich")
        missing_deps.append("rich")
    
    # 4. Mostrar instrucciones
    print()
    print("=" * 60)
    
    if missing_deps:
        print("⚠️  DEPENDENCIAS FALTANTES")
        print()
        print("Ejecuta el siguiente comando para instalarlas:")
        print()
        print(f"  pip install {' '.join(missing_deps)}")
        print()
        print("O instala todas con:")
        print()
        print("  pip install -r requirements.txt")
        print()
    else:
        print("✅ CONFIGURACIÓN COMPLETA")
        print()
        print("Ahora puedes:")
        print()
        print("1. Editar .env con la configuración de tu sistema:")
        print(f"   nano {env_file}")
        print()
        print("2. Colocar imágenes de prueba en:")
        print(f"   {images_dir}/")
        print()
        print("3. Ejecutar el simulador:")
        print("   python main.py")
        print()
    
    print("=" * 60)


if __name__ == "__main__":
    main()
