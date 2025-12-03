"""
Modelo de Tipo de Dispositivo
"""
from datetime import datetime
from ..extensions import db


class DeviceType(db.Model):
    __tablename__ = 'device_types'
    
    device_type_id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.Text, nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    devices = db.relationship('Device', backref='device_type', lazy='dynamic')
    
    def to_dict(self):
        return {
            'device_type_id': self.device_type_id,
            'type_name': self.type_name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<DeviceType {self.type_name}>'
