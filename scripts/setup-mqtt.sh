#!/bin/bash
#
# Script para generar credenciales MQTT
# Ejecutar ANTES de iniciar docker-compose
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MQTT_DIR="$(dirname "$SCRIPT_DIR")/mqtt"

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔐 Generando credenciales MQTT..."
echo ""

# Cargar variables de entorno si existen
if [ -f "$(dirname "$SCRIPT_DIR")/.env" ]; then
    source "$(dirname "$SCRIPT_DIR")/.env"
fi

# Contraseñas por defecto o desde .env
BACKEND_PASS="${MQTT_BACKEND_PASSWORD:-backend123}"
WORKER_PASS="${MQTT_WORKER_PASSWORD:-worker123}"
DEVICE_PASS="${MQTT_DEVICE_PASSWORD:-device123}"
CAMERA_PASS="${MQTT_CAMERA_PASSWORD:-camera123}"

# Verificar si Docker está disponible
if command -v docker &> /dev/null; then
    echo "Usando Docker para generar hashes..."
    
    # Crear archivo vacío
    > "$MQTT_DIR/passwd"
    
    # Generar contraseñas con Docker
    docker run --rm -v "$MQTT_DIR:/mosquitto/config" eclipse-mosquitto:2 \
        sh -c "mosquitto_passwd -c -b /mosquitto/config/passwd backend '$BACKEND_PASS' && \
               mosquitto_passwd -b /mosquitto/config/passwd worker '$WORKER_PASS' && \
               mosquitto_passwd -b /mosquitto/config/passwd device '$DEVICE_PASS' && \
               mosquitto_passwd -b /mosquitto/config/passwd camera '$CAMERA_PASS'"
    
    echo -e "${GREEN}✅ Credenciales generadas con hash${NC}"
    
elif command -v mosquitto_passwd &> /dev/null; then
    echo "Usando mosquitto_passwd local..."
    
    > "$MQTT_DIR/passwd"
    mosquitto_passwd -b "$MQTT_DIR/passwd" backend "$BACKEND_PASS"
    mosquitto_passwd -b "$MQTT_DIR/passwd" worker "$WORKER_PASS"
    mosquitto_passwd -b "$MQTT_DIR/passwd" device "$DEVICE_PASS"
    mosquitto_passwd -b "$MQTT_DIR/passwd" camera "$CAMERA_PASS"
    
    echo -e "${GREEN}✅ Credenciales generadas con hash${NC}"
    
else
    echo -e "${YELLOW}⚠️  Docker y mosquitto_passwd no disponibles${NC}"
    echo "Creando archivo con contraseñas en texto plano..."
    echo "(Mosquitto las hasheará al iniciar)"
    
    cat > "$MQTT_DIR/passwd" << EOF
backend:$BACKEND_PASS
worker:$WORKER_PASS
device:$DEVICE_PASS
camera:$CAMERA_PASS
EOF

    echo -e "${GREEN}✅ Credenciales creadas (texto plano)${NC}"
fi

echo ""
echo "Usuarios configurados:"
echo "  • backend: $BACKEND_PASS"
echo "  • worker: $WORKER_PASS"
echo "  • device: $DEVICE_PASS"
echo "  • camera: $CAMERA_PASS"
echo ""
echo "Archivo: $MQTT_DIR/passwd"
