--
-- Sistema de Seguridad IoT – Modelo de Base de Datos Final
-- PostgreSQL
--

------------------------------------------------------------
-- 1. Tabla: users
------------------------------------------------------------
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    email TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

------------------------------------------------------------
-- 2. Tabla: zones
------------------------------------------------------------
CREATE TABLE zones (
    zone_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (user_id, name)
);

------------------------------------------------------------
-- 3. Tabla: device_types
------------------------------------------------------------
CREATE TABLE device_types (
    device_type_id SERIAL PRIMARY KEY,
    type_name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

------------------------------------------------------------
-- 4. Tabla: devices
------------------------------------------------------------
CREATE TABLE devices (
    device_id SERIAL PRIMARY KEY,
    params JSONB,                                     -- Config AVANZADA en JSON
    name TEXT NOT NULL,
    description TEXT,
    device_type_id INT REFERENCES device_types(device_type_id),
    zone_id INT REFERENCES zones(zone_id) ON DELETE SET NULL,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    status BOOLEAN DEFAULT TRUE,                      -- Activo o inactivo
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (user_id, name)
);

------------------------------------------------------------
-- 5. Tabla: events
------------------------------------------------------------
CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    device_id INT REFERENCES devices(device_id) ON DELETE CASCADE NOT NULL,
    zone_id INT REFERENCES zones(zone_id) ON DELETE SET NULL,
    event_type TEXT NOT NULL,                         -- motion, relay_on, capture, error, etc.
    payload JSONB,                                    -- Datos adicionales del evento
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_events_zone_created ON events(zone_id, created_at);

------------------------------------------------------------
-- 6. Tabla: evidences (imágenes / videos)
------------------------------------------------------------
CREATE TABLE evidences (
    evidence_id SERIAL PRIMARY KEY,
    device_id INT REFERENCES devices(device_id) ON DELETE SET NULL,
    zone_id INT REFERENCES zones(zone_id) ON DELETE SET NULL,
    event_id INT REFERENCES events(event_id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,                          -- Ruta de imagen/video en disco
    ai_metadata JSONB,                                -- Resultados IA (opcional)
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_evidences_event ON evidences(event_id);
CREATE INDEX idx_evidences_zone ON evidences(zone_id);

------------------------------------------------------------
-- 7. Tabla: measurements (telemetría genérica)
------------------------------------------------------------
CREATE TABLE measurements (
    measurement_id SERIAL PRIMARY KEY,
    device_id INT REFERENCES devices(device_id) ON DELETE CASCADE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    recorded_at TIMESTAMP NOT NULL,
    data JSONB NOT NULL                               -- datos variables: temp, hum, voltajes, etc.
);

CREATE INDEX idx_measurements_recorded_at ON measurements(recorded_at);
CREATE INDEX idx_measurements_device_recorded ON measurements(device_id, recorded_at);

------------------------------------------------------------
-- 8. Datos iniciales recomendados
------------------------------------------------------------
INSERT INTO device_types (type_name, description) VALUES
('pir', 'Sensor de movimiento PIR'),
('camera', 'Cámara ESP32-CAM o RPi Zero'),
('relay', 'Módulo de relé'),
('sensor', 'Sensor genérico'),
('telemetry', 'Fuente de datos de telemetría');

------------------------------------------------------------
-- FIN DEL DOCUMENTO
------------------------------------------------------------
