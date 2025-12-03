"""
Conexión a base de datos para el servicio de IA
"""
import json
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool

from config import config

logger = logging.getLogger('ai-service.database')


class Database:
    """Gestión de conexión a PostgreSQL"""
    
    def __init__(self):
        self.engine = None
    
    def connect(self):
        """Establecer conexión"""
        try:
            self.engine = create_engine(
                config.DATABASE_URL,
                poolclass=QueuePool,
                pool_size=3,
                max_overflow=5,
                pool_pre_ping=True
            )
            
            # Verificar conexión
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info("Conexión a base de datos establecida")
            
        except Exception as e:
            logger.error(f"Error al conectar a BD: {e}")
            raise
    
    def close(self):
        """Cerrar conexión"""
        if self.engine:
            self.engine.dispose()
    
    def update_evidence_ai_metadata(self, evidence_id: int, ai_result: dict):
        """
        Actualizar evidencia con resultados de IA
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(
                    text("""
                        UPDATE evidences 
                        SET ai_metadata = CAST(:ai_metadata AS jsonb)
                        WHERE evidence_id = :evidence_id
                    """),
                    {
                        'evidence_id': evidence_id,
                        'ai_metadata': json.dumps(ai_result)
                    }
                )
                conn.commit()
            
            logger.info(f"Evidencia {evidence_id} actualizada con IA metadata")
            
        except Exception as e:
            logger.error(f"Error actualizando evidencia: {e}")
            raise
    
    def get_pending_evidences(self, limit: int = 10):
        """
        Obtener evidencias pendientes de análisis
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("""
                        SELECT evidence_id, file_path, device_id, zone_id
                        FROM evidences
                        WHERE ai_metadata IS NULL
                        ORDER BY created_at DESC
                        LIMIT :limit
                    """),
                    {'limit': limit}
                )
                return [dict(row._mapping) for row in result]
        except Exception as e:
            logger.error(f"Error obteniendo evidencias pendientes: {e}")
            return []
