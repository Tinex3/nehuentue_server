"""
Modelo de Dispositivo
"""
from datetime import datetime
from ..extensions import db


class Device(db.Model):
    __tablename__ = 'devices'
    
    device_id = db.Column(db.Integer, primary_key=True)
    params = db.Column(db.JSON, default={})  # Config avanzada en JSON
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    device_type_id = db.Column(db.Integer, db.ForeignKey('device_types.device_type_id'))
    zone_id = db.Column(db.Integer, db.ForeignKey('zones.zone_id', ondelete='SET NULL'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'))
    status = db.Column(db.Boolean, default=True)  # Activo o inactivo
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Constraint único compuesto
    __table_args__ = (
        db.UniqueConstraint('user_id', 'name', name='uq_device_user_name'),
    )
    
    # Relaciones
    events = db.relationship('Event', backref='device', lazy='dynamic', cascade='all, delete-orphan')
    evidences = db.relationship('Evidence', backref='device', lazy='dynamic')
    measurements = db.relationship('Measurement', backref='device', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_params=True):
        data = {
            'device_id': self.device_id,
            'name': self.name,
            'description': self.description,
            'device_type_id': self.device_type_id,
            'device_type': self.device_type.type_name if self.device_type else None,
            'zone_id': self.zone_id,
            'zone_name': self.zone.name if self.zone else None,
            'user_id': self.user_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_params:
            data['params'] = self.params
        return data
    
    def __repr__(self):
        return f'<Device {self.name}>'
