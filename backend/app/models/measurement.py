"""
Modelo de Medición (telemetría)
"""
from datetime import datetime
from ..extensions import db


class Measurement(db.Model):
    __tablename__ = 'measurements'
    
    measurement_id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.device_id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    recorded_at = db.Column(db.DateTime, nullable=False)  # Timestamp del dispositivo
    data = db.Column(db.JSON, nullable=False)  # Datos: temp, hum, voltajes, etc.
    
    # Índices
    __table_args__ = (
        db.Index('idx_measurements_recorded_at', 'recorded_at'),
        db.Index('idx_measurements_device_recorded', 'device_id', 'recorded_at'),
    )
    
    def to_dict(self):
        return {
            'measurement_id': self.measurement_id,
            'device_id': self.device_id,
            'device_name': self.device.name if self.device else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
            'data': self.data
        }
    
    def __repr__(self):
        return f'<Measurement {self.measurement_id} device={self.device_id}>'
