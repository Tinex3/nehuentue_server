"""
Worker MQTT - Procesador de eventos IoT
Sistema de Seguridad IoT
"""
import os
import sys
import signal
import logging
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('worker')

from mqtt_handler import MQTTHandler
from database import Database

# Variables globales
mqtt_handler = None
db = None
running = True


def signal_handler(signum, frame):
    """Manejador de señales para shutdown graceful"""
    global running
    logger.info(f"Señal {signum} recibida, cerrando worker...")
    running = False
    
    if mqtt_handler:
        mqtt_handler.stop()


def main():
    global mqtt_handler, db
    
    logger.info("=" * 50)
    logger.info("Iniciando Worker MQTT - Sistema de Seguridad IoT")
    logger.info("=" * 50)
    
    # Registrar manejadores de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Inicializar base de datos
        logger.info("Conectando a la base de datos...")
        db = Database()
        db.connect()
        logger.info("Base de datos conectada")
        
        # Inicializar y conectar MQTT
        logger.info("Conectando al broker MQTT...")
        mqtt_handler = MQTTHandler(db)
        mqtt_handler.start()
        logger.info("Worker MQTT iniciado correctamente")
        
        # Loop principal
        while running:
            signal.pause()
            
    except KeyboardInterrupt:
        logger.info("Interrupción de teclado recibida")
    except Exception as e:
        logger.error(f"Error fatal: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Cerrando conexiones...")
        if mqtt_handler:
            mqtt_handler.stop()
        if db:
            db.close()
        logger.info("Worker finalizado")


if __name__ == '__main__':
    main()
