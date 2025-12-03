"""
Schemas Marshmallow para serialización y validación
"""
from .user import UserSchema, UserCreateSchema, UserLoginSchema
from .zone import ZoneSchema, ZoneCreateSchema
from .device_type import DeviceTypeSchema
from .device import DeviceSchema, DeviceCreateSchema, DeviceUpdateSchema
from .event import EventSchema
from .evidence import EvidenceSchema
from .measurement import MeasurementSchema, MeasurementCreateSchema

__all__ = [
    'UserSchema', 'UserCreateSchema', 'UserLoginSchema',
    'ZoneSchema', 'ZoneCreateSchema',
    'DeviceTypeSchema',
    'DeviceSchema', 'DeviceCreateSchema', 'DeviceUpdateSchema',
    'EventSchema',
    'EvidenceSchema',
    'MeasurementSchema', 'MeasurementCreateSchema'
]
