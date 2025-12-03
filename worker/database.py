"""
Conexión a base de datos PostgreSQL
"""
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool

from config import config

logger = logging.getLogger('worker.database')


class Database:
    """Gestión de conexión a PostgreSQL"""
    
    def __init__(self):
        self.engine = None
        self.Session = None
    
    def connect(self):
        """Establecer conexión a la base de datos"""
        try:
            self.engine = create_engine(
                config.DATABASE_URL,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                pool_recycle=300
            )
            
            # Crear session factory
            session_factory = sessionmaker(bind=self.engine)
            self.Session = scoped_session(session_factory)
            
            # Verificar conexión
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info("Conexión a base de datos establecida")
            
        except Exception as e:
            logger.error(f"Error al conectar a la base de datos: {e}")
            raise
    
    def close(self):
        """Cerrar conexión"""
        if self.Session:
            self.Session.remove()
        if self.engine:
            self.engine.dispose()
        logger.info("Conexión a base de datos cerrada")
    
    def get_session(self):
        """Obtener sesión de base de datos"""
        return self.Session()
    
    # ==================== QUERIES ====================
    
    def get_device_by_id(self, device_id: int) -> dict:
        """Obtener dispositivo por ID"""
        session = self.get_session()
        try:
            result = session.execute(
                text("""
                    SELECT d.*, dt.type_name, z.name as zone_name
                    FROM devices d
                    LEFT JOIN device_types dt ON d.device_type_id = dt.device_type_id
                    LEFT JOIN zones z ON d.zone_id = z.zone_id
                    WHERE d.device_id = :device_id
                """),
                {'device_id': device_id}
            )
            row = result.fetchone()
            return dict(row._mapping) if row else None
        finally:
            session.close()
    
    def get_devices_by_zone(self, zone_id: int, device_type: str = None) -> list:
        """Obtener dispositivos de una zona, opcionalmente filtrado por tipo"""
        session = self.get_session()
        try:
            query = """
                SELECT d.*, dt.type_name
                FROM devices d
                LEFT JOIN device_types dt ON d.device_type_id = dt.device_type_id
                WHERE d.zone_id = :zone_id AND d.status = true
            """
            params = {'zone_id': zone_id}
            
            if device_type:
                query += " AND dt.type_name = :device_type"
                params['device_type'] = device_type
            
            result = session.execute(text(query), params)
            return [dict(row._mapping) for row in result]
        finally:
            session.close()
    
    def get_zone_by_device(self, device_id: int) -> dict:
        """Obtener zona de un dispositivo"""
        session = self.get_session()
        try:
            result = session.execute(
                text("""
                    SELECT z.*
                    FROM zones z
                    JOIN devices d ON d.zone_id = z.zone_id
                    WHERE d.device_id = :device_id
                """),
                {'device_id': device_id}
            )
            row = result.fetchone()
            return dict(row._mapping) if row else None
        finally:
            session.close()
    
    def create_event(self, device_id: int, zone_id: int, event_type: str, payload: dict = None) -> int:
        """Crear nuevo evento"""
        session = self.get_session()
        try:
            result = session.execute(
                text("""
                    INSERT INTO events (device_id, zone_id, event_type, payload)
                    VALUES (:device_id, :zone_id, :event_type, :payload::jsonb)
                    RETURNING event_id
                """),
                {
                    'device_id': device_id,
                    'zone_id': zone_id,
                    'event_type': event_type,
                    'payload': str(payload) if payload else '{}'
                }
            )
            event_id = result.fetchone()[0]
            session.commit()
            logger.info(f"Evento creado: {event_type} (ID: {event_id})")
            return event_id
        except Exception as e:
            session.rollback()
            logger.error(f"Error al crear evento: {e}")
            raise
        finally:
            session.close()
    
    def create_evidence(self, device_id: int, zone_id: int, event_id: int, 
                       file_path: str, ai_metadata: dict = None) -> int:
        """Crear nueva evidencia"""
        session = self.get_session()
        try:
            result = session.execute(
                text("""
                    INSERT INTO evidences (device_id, zone_id, event_id, file_path, ai_metadata)
                    VALUES (:device_id, :zone_id, :event_id, :file_path, :ai_metadata::jsonb)
                    RETURNING evidence_id
                """),
                {
                    'device_id': device_id,
                    'zone_id': zone_id,
                    'event_id': event_id,
                    'file_path': file_path,
                    'ai_metadata': str(ai_metadata) if ai_metadata else None
                }
            )
            evidence_id = result.fetchone()[0]
            session.commit()
            logger.info(f"Evidencia creada (ID: {evidence_id})")
            return evidence_id
        except Exception as e:
            session.rollback()
            logger.error(f"Error al crear evidencia: {e}")
            raise
        finally:
            session.close()
    
    def create_measurement(self, device_id: int, recorded_at: str, data: dict) -> int:
        """Crear nueva medición de telemetría"""
        session = self.get_session()
        try:
            result = session.execute(
                text("""
                    INSERT INTO measurements (device_id, recorded_at, data)
                    VALUES (:device_id, :recorded_at, :data::jsonb)
                    RETURNING measurement_id
                """),
                {
                    'device_id': device_id,
                    'recorded_at': recorded_at,
                    'data': str(data).replace("'", '"')
                }
            )
            measurement_id = result.fetchone()[0]
            session.commit()
            return measurement_id
        except Exception as e:
            session.rollback()
            logger.error(f"Error al crear medición: {e}")
            raise
        finally:
            session.close()
    
    def update_device_status(self, device_id: int, status: bool):
        """Actualizar estado de dispositivo"""
        session = self.get_session()
        try:
            session.execute(
                text("""
                    UPDATE devices SET status = :status WHERE device_id = :device_id
                """),
                {'device_id': device_id, 'status': status}
            )
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error al actualizar estado: {e}")
        finally:
            session.close()
    
    def get_last_motion_event(self, zone_id: int) -> dict:
        """Obtener último evento de movimiento en una zona"""
        session = self.get_session()
        try:
            result = session.execute(
                text("""
                    SELECT * FROM events
                    WHERE zone_id = :zone_id AND event_type = 'motion'
                    ORDER BY created_at DESC
                    LIMIT 1
                """),
                {'zone_id': zone_id}
            )
            row = result.fetchone()
            return dict(row._mapping) if row else None
        finally:
            session.close()
