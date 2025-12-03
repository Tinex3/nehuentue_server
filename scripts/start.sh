#!/bin/bash
#
# Script de inicio del Sistema de Seguridad IoT
# Uso: ./scripts/start.sh [opción]
#
# Opciones:
#   --build    Reconstruir imágenes antes de iniciar
#   --dev      Modo desarrollo (con logs)
#   --stop     Detener todos los servicios
#   --restart  Reiniciar todos los servicios
#   --logs     Ver logs en tiempo real
#   --status   Ver estado de los servicios
#

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directorio base del proyecto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Funciones de utilidad
print_header() {
    echo -e "\n${BLUE}=================================================${NC}"
    echo -e "${BLUE}  🔐 Sistema de Seguridad IoT${NC}"
    echo -e "${BLUE}=================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Verificar prerequisitos
check_prerequisites() {
    echo "Verificando prerequisitos..."
    
    # Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker no está instalado"
        exit 1
    fi
    print_success "Docker instalado"
    
    # Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose no está instalado"
        exit 1
    fi
    print_success "Docker Compose instalado"
    
    # Archivo .env
    if [ ! -f ".env" ]; then
        print_warning "Archivo .env no encontrado"
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_info "Creado .env desde .env.example"
            print_warning "¡Edita .env con tus credenciales antes de continuar!"
        fi
    else
        print_success "Archivo .env encontrado"
    fi
    
    # Credenciales MQTT
    if [ ! -s "mqtt/passwd" ]; then
        print_warning "Credenciales MQTT vacías"
        print_info "Ejecutando configuración de MQTT..."
        setup_mqtt
    else
        print_success "Credenciales MQTT configuradas"
    fi
    
    echo ""
}

# Configurar credenciales MQTT
setup_mqtt() {
    echo ""
    print_info "Configurando credenciales MQTT..."
    
    # Crear archivo de contraseñas
    MQTT_PASSWD_FILE="mqtt/passwd"
    
    # Generar contraseñas por defecto o usar las del .env
    source .env 2>/dev/null || true
    
    BACKEND_PASS="${MQTT_BACKEND_PASSWORD:-backend123}"
    WORKER_PASS="${MQTT_WORKER_PASSWORD:-worker123}"
    DEVICE_PASS="${MQTT_DEVICE_PASSWORD:-device123}"
    CAMERA_PASS="${MQTT_CAMERA_PASSWORD:-camera123}"
    
    # Crear archivo temporal
    TEMP_FILE=$(mktemp)
    echo "backend:${BACKEND_PASS}" > "$TEMP_FILE"
    echo "worker:${WORKER_PASS}" >> "$TEMP_FILE"
    echo "device:${DEVICE_PASS}" >> "$TEMP_FILE"
    echo "camera:${CAMERA_PASS}" >> "$TEMP_FILE"
    
    # Usar mosquitto_passwd si está disponible, sino formato plano
    if command -v mosquitto_passwd &> /dev/null; then
        # Crear con hash
        > "$MQTT_PASSWD_FILE"
        mosquitto_passwd -b "$MQTT_PASSWD_FILE" backend "$BACKEND_PASS"
        mosquitto_passwd -b "$MQTT_PASSWD_FILE" worker "$WORKER_PASS"
        mosquitto_passwd -b "$MQTT_PASSWD_FILE" device "$DEVICE_PASS"
        mosquitto_passwd -b "$MQTT_PASSWD_FILE" camera "$CAMERA_PASS"
    else
        # Crear usando Docker
        docker run --rm -v "$PROJECT_DIR/mqtt:/mosquitto/config" \
            eclipse-mosquitto:2 \
            sh -c "mosquitto_passwd -c -b /mosquitto/config/passwd backend '$BACKEND_PASS' && \
                   mosquitto_passwd -b /mosquitto/config/passwd worker '$WORKER_PASS' && \
                   mosquitto_passwd -b /mosquitto/config/passwd device '$DEVICE_PASS' && \
                   mosquitto_passwd -b /mosquitto/config/passwd camera '$CAMERA_PASS'"
    fi
    
    rm -f "$TEMP_FILE"
    
    print_success "Credenciales MQTT configuradas"
    echo ""
    echo "  Usuarios creados:"
    echo "    - backend: $BACKEND_PASS"
    echo "    - worker: $WORKER_PASS"
    echo "    - device: $DEVICE_PASS"
    echo "    - camera: $CAMERA_PASS"
    echo ""
}

# Iniciar servicios
start_services() {
    local BUILD_FLAG=""
    
    if [ "$1" == "--build" ]; then
        BUILD_FLAG="--build"
        print_info "Reconstruyendo imágenes..."
    fi
    
    echo "Iniciando servicios..."
    
    # Usar docker compose (v2) o docker-compose (v1)
    if docker compose version &> /dev/null; then
        docker compose up -d $BUILD_FLAG
    else
        docker-compose up -d $BUILD_FLAG
    fi
    
    print_success "Servicios iniciados"
    
    # Esperar a que los servicios estén listos
    echo ""
    print_info "Esperando a que los servicios estén listos..."
    sleep 5
    
    show_status
    show_urls
}

# Detener servicios
stop_services() {
    echo "Deteniendo servicios..."
    
    if docker compose version &> /dev/null; then
        docker compose down
    else
        docker-compose down
    fi
    
    print_success "Servicios detenidos"
}

# Reiniciar servicios
restart_services() {
    stop_services
    echo ""
    start_services
}

# Ver logs
show_logs() {
    local SERVICE="$1"
    
    if [ -n "$SERVICE" ]; then
        if docker compose version &> /dev/null; then
            docker compose logs -f "$SERVICE"
        else
            docker-compose logs -f "$SERVICE"
        fi
    else
        if docker compose version &> /dev/null; then
            docker compose logs -f
        else
            docker-compose logs -f
        fi
    fi
}

# Ver estado
show_status() {
    echo ""
    echo "Estado de los servicios:"
    echo "------------------------"
    
    if docker compose version &> /dev/null; then
        docker compose ps
    else
        docker-compose ps
    fi
}

# Mostrar URLs
show_urls() {
    echo ""
    echo "🌐 URLs de acceso:"
    echo "   Frontend:     http://localhost"
    echo "   Backend API:  http://localhost:5000/api"
    echo "   AI Service:   http://localhost:5001"
    echo "   MQTT Broker:  localhost:1883"
    echo "   PostgreSQL:   localhost:5432"
    echo ""
    echo "📝 Usuario de prueba:"
    echo "   Email:    benjamin@benjamin.cl"
    echo "   Password: 12345678"
    echo ""
}

# Menú principal
show_help() {
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos:"
    echo "  start         Iniciar todos los servicios"
    echo "  start --build Iniciar y reconstruir imágenes"
    echo "  stop          Detener todos los servicios"
    echo "  restart       Reiniciar todos los servicios"
    echo "  status        Ver estado de los servicios"
    echo "  logs          Ver logs de todos los servicios"
    echo "  logs <srv>    Ver logs de un servicio específico"
    echo "  setup-mqtt    Configurar credenciales MQTT"
    echo "  urls          Mostrar URLs de acceso"
    echo "  help          Mostrar esta ayuda"
    echo ""
    echo "Servicios disponibles:"
    echo "  db, mqtt, backend, worker, ai, frontend"
    echo ""
}

# Main
print_header

case "${1:-start}" in
    start)
        check_prerequisites
        start_services "$2"
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$2"
        ;;
    setup-mqtt)
        setup_mqtt
        ;;
    urls)
        show_urls
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Comando desconocido: $1"
        show_help
        exit 1
        ;;
esac
