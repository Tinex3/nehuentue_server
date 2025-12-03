#!/bin/bash
#
# Script rápido para desarrollo local
# Inicia solo los servicios esenciales sin Docker
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  🔧 Desarrollo Local - IoT Security${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Verificar .env
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Creado .env - edita las credenciales${NC}"
fi

source .env 2>/dev/null || true

case "${1:-help}" in
    mqtt)
        echo "🦟 Iniciando Mosquitto MQTT..."
        docker run -d --name iot_mqtt_dev \
            -p 1883:1883 \
            -p 9001:9001 \
            -v "$PROJECT_DIR/mqtt/mosquitto.conf:/mosquitto/config/mosquitto.conf:ro" \
            -v "$PROJECT_DIR/mqtt/acl:/mosquitto/config/acl:ro" \
            -v "$PROJECT_DIR/mqtt/passwd:/mosquitto/config/passwd:ro" \
            eclipse-mosquitto:2
        echo -e "${GREEN}✅ MQTT corriendo en localhost:1883${NC}"
        ;;
    
    db)
        echo "🐘 Iniciando PostgreSQL..."
        docker run -d --name iot_db_dev \
            -p 5432:5432 \
            -e POSTGRES_DB=${POSTGRES_DB:-iot_security} \
            -e POSTGRES_USER=${POSTGRES_USER:-iot_user} \
            -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-iot_password} \
            -v "$PROJECT_DIR/database/init.sql:/docker-entrypoint-initdb.d/init.sql:ro" \
            postgres:15-alpine
        echo -e "${GREEN}✅ PostgreSQL corriendo en localhost:5432${NC}"
        ;;
    
    backend)
        echo "🐍 Iniciando Backend Flask..."
        cd backend
        if [ ! -d "venv" ]; then
            python3 -m venv venv
            source venv/bin/activate
            pip install -r requirements.txt
        else
            source venv/bin/activate
        fi
        export FLASK_ENV=development
        export DATABASE_URL="postgresql://${POSTGRES_USER:-iot_user}:${POSTGRES_PASSWORD:-iot_password}@localhost:5432/${POSTGRES_DB:-iot_security}"
        python run.py
        ;;
    
    worker)
        echo "⚙️ Iniciando Worker MQTT..."
        cd worker
        if [ ! -d "venv" ]; then
            python3 -m venv venv
            source venv/bin/activate
            pip install -r requirements.txt
        else
            source venv/bin/activate
        fi
        export DATABASE_URL="postgresql://${POSTGRES_USER:-iot_user}:${POSTGRES_PASSWORD:-iot_password}@localhost:5432/${POSTGRES_DB:-iot_security}"
        export MQTT_BROKER=localhost
        python main.py
        ;;
    
    ai)
        echo "🤖 Iniciando Servicio de IA..."
        cd ai
        if [ ! -d "venv" ]; then
            python3 -m venv venv
            source venv/bin/activate
            pip install -r requirements.txt
        else
            source venv/bin/activate
        fi
        export DATABASE_URL="postgresql://${POSTGRES_USER:-iot_user}:${POSTGRES_PASSWORD:-iot_password}@localhost:5432/${POSTGRES_DB:-iot_security}"
        python app.py
        ;;
    
    frontend)
        echo "⚛️ Iniciando Frontend React..."
        cd frontend
        npm run dev
        ;;
    
    stop)
        echo "🛑 Deteniendo contenedores de desarrollo..."
        docker stop iot_mqtt_dev iot_db_dev 2>/dev/null || true
        docker rm iot_mqtt_dev iot_db_dev 2>/dev/null || true
        echo -e "${GREEN}✅ Contenedores detenidos${NC}"
        ;;
    
    *)
        echo "Uso: $0 <servicio>"
        echo ""
        echo "Servicios disponibles:"
        echo "  mqtt      - Iniciar solo MQTT broker"
        echo "  db        - Iniciar solo PostgreSQL"
        echo "  backend   - Iniciar Backend Flask"
        echo "  worker    - Iniciar Worker MQTT"
        echo "  ai        - Iniciar Servicio IA"
        echo "  frontend  - Iniciar Frontend React"
        echo "  stop      - Detener servicios Docker"
        echo ""
        echo "Ejemplo de flujo de desarrollo:"
        echo "  Terminal 1: ./scripts/dev.sh db"
        echo "  Terminal 2: ./scripts/dev.sh mqtt"
        echo "  Terminal 3: ./scripts/dev.sh backend"
        echo "  Terminal 4: ./scripts/dev.sh frontend"
        ;;
esac
