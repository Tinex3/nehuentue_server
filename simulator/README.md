# Simulador IoT - Sistema de Seguridad

Simulador de dispositivos IoT para probar el sistema desde tu PC sin hardware real.

## 🚀 Instalación

```bash
cd simulator

# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o: venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configuración inicial
python main.py setup
```

## ⚙️ Configuración

Edita el archivo `.env` con tu configuración:

```env
# MQTT Broker
MQTT_BROKER=localhost        # IP del broker (localhost o IP de RPI)
MQTT_PORT=1883
MQTT_USER=iot_system
MQTT_PASSWORD=iot_password_123

# API Services
API_URL=http://localhost:5000/api
AI_SERVICE_URL=http://localhost:5001

# Dispositivo simulado
DEVICE_ID=1                  # ID del dispositivo a simular
ZONE_ID=1                    # ID de la zona
```

## 📋 Comandos Disponibles

### Configuración y Estado

```bash
# Configuración inicial (crea carpetas y archivos)
python main.py setup

# Ver estado de los servicios
python main.py status

# Probar conexión MQTT
python main.py test-mqtt
```

### Simular Eventos

```bash
# Enviar evento de movimiento (PIR)
python main.py send-motion

# Enviar 5 eventos con 3 segundos de intervalo
python main.py send-motion -c 5 -i 3

# Enviar telemetría (temperatura, humedad)
python main.py send-telemetry

# Enviar con valores específicos
python main.py send-telemetry -t 25.5 -u 60
```

### Enviar Imágenes

```bash
# Enviar imagen específica
python main.py send-image -f /ruta/a/imagen.jpg

# Enviar todas las imágenes de una carpeta
python main.py send-image -d ./images

# Enviar imágenes sin evento de movimiento previo
python main.py send-image -d ./images --no-motion

# Enviar con intervalo de 5 segundos
python main.py send-image -d ./images -i 5
```

### Detección de IA (Sin MQTT)

```bash
# Probar detección en una imagen
python main.py ai-detect -f foto.jpg

# Procesar carpeta completa
python main.py ai-detect -d ./images
```

### Modo Continuo

Simula un sensor activo enviando datos periódicamente:

```bash
# Modo básico
python main.py continuous

# Con configuración personalizada
python main.py continuous \
  --telemetry-interval 60 \
  --motion-probability 0.2 \
  --images-folder ./images
```

## 📁 Estructura de Imágenes

Coloca tus imágenes de prueba en la carpeta `./images`:

```
simulator/
├── images/
│   ├── persona1.jpg
│   ├── persona2.jpg
│   ├── carro.jpg
│   └── vacio.jpg
├── main.py
├── mqtt_simulator.py
├── api_client.py
└── .env
```

## 🔄 Flujo de Datos

Cuando envías una imagen:

1. **Evento de Movimiento** → `events/motion`
   ```json
   {
     "device_id": 1,
     "zone_id": 1,
     "timestamp": "2024-01-15T10:30:00Z",
     "confidence": 0.95
   }
   ```

2. **Frame de Cámara** → `cameras/1/frame`
   ```json
   {
     "device_id": 1,
     "zone_id": 1,
     "timestamp": "2024-01-15T10:30:01Z",
     "image": "base64...",
     "format": "jpg"
   }
   ```

3. **Worker procesa** → Guarda imagen → Llama a AI Service

4. **AI Service analiza** → Actualiza `ai_metadata`

5. **Frontend muestra** → Evidencia con detecciones

## 🧪 Ejemplo de Prueba Completa

```bash
# 1. Verificar servicios
python main.py status

# 2. Probar conexión MQTT
python main.py test-mqtt

# 3. Enviar evento de movimiento
python main.py send-motion

# 4. Enviar imagen para análisis
python main.py send-image -f ./images/test.jpg

# 5. Ver detecciones localmente (sin MQTT)
python main.py ai-detect -f ./images/test.jpg

# 6. Modo continuo para pruebas largas
python main.py continuous --telemetry-interval 30
```

## 🖼️ Imágenes de Prueba Recomendadas

Para probar el sistema de detección:

- **Personas**: Fotos con 1-5 personas visibles
- **Vacías**: Fotos sin personas (para false positives)
- **Vehículos**: Autos, motos (detectados por el modelo)
- **Animales**: Perros, gatos (detectados por el modelo)
- **Mixtas**: Escenas con múltiples objetos

## 🐛 Troubleshooting

### Error: No se puede conectar a MQTT
```bash
# Verificar que el broker esté corriendo
docker ps | grep mosquitto

# O iniciar manualmente
docker-compose up -d mqtt
```

### Error: AI Service no disponible
```bash
# Verificar servicio de IA
curl http://localhost:5001/health

# Iniciar si no está corriendo
docker-compose up -d ai
```

### Error: Imagen no encontrada
```bash
# Verificar ruta absoluta o relativa
ls -la ./images/
python main.py send-image -f "$(pwd)/images/foto.jpg"
```

## 📊 Ver Resultados

1. **Frontend**: http://localhost:3000
   - Dashboard: Eventos recientes
   - Evidencias: Galería con análisis IA
   - Telemetría: Gráficos de temperatura

2. **Logs del Worker**:
   ```bash
   docker-compose logs -f worker
   ```

3. **Base de datos**:
   ```bash
   docker exec -it postgres psql -U postgres -d iot_security
   SELECT * FROM events ORDER BY created_at DESC LIMIT 10;
   SELECT * FROM evidences ORDER BY created_at DESC LIMIT 5;
   ```
