# Sistema de Seguridad IoT

## Estructura del Proyecto

```
proyecto/
├── docker-compose.yml          # Orquestación de contenedores
├── .env.example                 # Variables de entorno (ejemplo)
├── .env                         # Variables de entorno (crear desde .env.example)
│
├── backend/                     # API REST Flask
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/                     # Código fuente
│
├── worker/                      # Worker MQTT
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
│
├── ai/                          # Servicio de IA
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py
│   └── models/                  # Modelos TFLite
│
├── frontend/                    # Dashboard React
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── src/
│
├── mqtt/                        # Configuración Mosquitto
│   ├── mosquitto.conf
│   ├── acl
│   └── passwd
│
├── database/                    # Scripts SQL
│   └── init.sql
│
└── output/                      # Documentación PDF
```

## Requisitos

- Docker >= 20.10
- Docker Compose >= 2.0
- Node.js >= 18 (para desarrollo frontend)
- Python >= 3.11 (para desarrollo local)

## Inicio Rápido

### 1. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con valores seguros
```

### 2. Generar contraseñas MQTT

```bash
# Crear archivo de contraseñas vacío primero
touch mqtt/passwd

# Levantar solo el broker MQTT
docker-compose up -d mqtt

# Generar contraseñas encriptadas
docker exec iot_mqtt mosquitto_passwd -c /mosquitto/config/passwd backend
docker exec iot_mqtt mosquitto_passwd /mosquitto/config/passwd worker
docker exec iot_mqtt mosquitto_passwd /mosquitto/config/passwd device
docker exec iot_mqtt mosquitto_passwd /mosquitto/config/passwd camera

# Reiniciar el broker
docker-compose restart mqtt
```

### 3. Levantar todos los servicios

```bash
docker-compose up -d
```

### 4. Verificar estado

```bash
docker-compose ps
docker-compose logs -f
```

## Servicios

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| Frontend | 80 | Dashboard React |
| Backend | 5000 | API REST Flask |
| AI | 5001 | Servicio de detección |
| MQTT | 1883 | Broker MQTT |
| MQTT WS | 9001 | MQTT WebSocket |
| PostgreSQL | 5432 | Base de datos |

## API Endpoints

### Autenticación
- `POST /api/auth/login` - Iniciar sesión
- `POST /api/auth/register` - Registrar usuario
- `POST /api/auth/refresh` - Refrescar token

### Zonas
- `GET /api/zones` - Listar zonas
- `POST /api/zones` - Crear zona
- `GET /api/zones/:id` - Obtener zona
- `PUT /api/zones/:id` - Actualizar zona
- `DELETE /api/zones/:id` - Eliminar zona

### Dispositivos
- `GET /api/devices` - Listar dispositivos
- `POST /api/devices` - Registrar dispositivo
- `GET /api/devices/:id` - Obtener dispositivo
- `PUT /api/devices/:id` - Actualizar dispositivo
- `DELETE /api/devices/:id` - Eliminar dispositivo
- `POST /api/devices/:id/command` - Enviar comando

### Eventos
- `GET /api/events` - Listar eventos
- `GET /api/events/:id` - Obtener evento
- `PUT /api/events/:id/acknowledge` - Reconocer evento

### Evidencias
- `GET /api/evidences` - Listar evidencias
- `GET /api/evidences/:id` - Obtener evidencia
- `GET /api/evidences/:id/file` - Descargar archivo

### Mediciones
- `GET /api/measurements` - Listar mediciones
- `GET /api/measurements/device/:id` - Mediciones por dispositivo

## Tópicos MQTT

### Publicación (Dispositivos → Sistema)
- `devices/{device_id}/status` - Estado del dispositivo
- `devices/{device_id}/telemetry` - Datos de telemetría
- `events/motion` - Eventos de movimiento PIR
- `cameras/{camera_id}/frame` - Frames de cámara

### Suscripción (Sistema → Dispositivos)
- `commands/{device_id}/#` - Comandos para dispositivo
- `commands/cameras/{camera_id}` - Comandos para cámara
- `commands/relays/{relay_id}` - Comandos para relé

## Desarrollo

### Backend (Flask)
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask run --debug
```

### Frontend (React)
```bash
cd frontend
npm install
npm run dev
```

### Worker MQTT
```bash
cd worker
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Licencia

MIT
