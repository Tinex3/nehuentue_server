"""
Modelo de Zona
"""
from datetime import datetime
from ..extensions import db


class Zone(db.Model):
    __tablename__ = 'zones'
    
    zone_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'))
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Constraint único compuesto
    __table_args__ = (
        db.UniqueConstraint('user_id', 'name', name='uq_zone_user_name'),
    )
    
    # Relaciones
    devices = db.relationship('Device', backref='zone', lazy='dynamic')
    events = db.relationship('Event', backref='zone', lazy='dynamic')
    evidences = db.relationship('Evidence', backref='zone', lazy='dynamic')
    
    def to_dict(self, include_devices=False):
        data = {
            'zone_id': self.zone_id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'device_count': self.devices.count()
        }
        if include_devices:
            data['devices'] = [d.to_dict() for d in self.devices]
        return data
    
    def __repr__(self):
        return f'<Zone {self.name}>'
