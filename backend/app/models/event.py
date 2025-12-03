"""
Modelo de Evento
"""
from datetime import datetime
from ..extensions import db


class Event(db.Model):
    __tablename__ = 'events'
    
    event_id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.device_id', ondelete='CASCADE'), nullable=False)
    zone_id = db.Column(db.Integer, db.ForeignKey('zones.zone_id', ondelete='SET NULL'))
    event_type = db.Column(db.Text, nullable=False)  # motion, relay_on, capture, error, etc.
    payload = db.Column(db.JSON)  # Datos adicionales del evento
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Índice compuesto
    __table_args__ = (
        db.Index('idx_events_zone_created', 'zone_id', 'created_at'),
    )
    
    # Relaciones
    evidences = db.relationship('Evidence', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_evidences=False):
        data = {
            'event_id': self.event_id,
            'device_id': self.device_id,
            'device_name': self.device.name if self.device else None,
            'zone_id': self.zone_id,
            'zone_name': self.zone.name if self.zone else None,
            'event_type': self.event_type,
            'payload': self.payload,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'evidence_count': self.evidences.count()
        }
        if include_evidences:
            data['evidences'] = [e.to_dict() for e in self.evidences]
        return data
    
    def __repr__(self):
        return f'<Event {self.event_type} device={self.device_id}>'
