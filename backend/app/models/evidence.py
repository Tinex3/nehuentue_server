"""
Modelo de Evidencia (imágenes/videos)
"""
from datetime import datetime
from ..extensions import db


class Evidence(db.Model):
    __tablename__ = 'evidences'
    
    evidence_id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.device_id', ondelete='SET NULL'))
    zone_id = db.Column(db.Integer, db.ForeignKey('zones.zone_id', ondelete='SET NULL'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id', ondelete='CASCADE'))
    file_path = db.Column(db.Text, nullable=False)  # Ruta de imagen/video en disco
    ai_metadata = db.Column(db.JSON)  # Resultados IA (opcional)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Índices
    __table_args__ = (
        db.Index('idx_evidences_event', 'event_id'),
        db.Index('idx_evidences_zone', 'zone_id'),
    )
    
    def to_dict(self, include_ai=True):
        data = {
            'evidence_id': self.evidence_id,
            'device_id': self.device_id,
            'zone_id': self.zone_id,
            'event_id': self.event_id,
            'file_path': self.file_path,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_ai:
            data['ai_metadata'] = self.ai_metadata
        return data
    
    def __repr__(self):
        return f'<Evidence {self.evidence_id} event={self.event_id}>'
