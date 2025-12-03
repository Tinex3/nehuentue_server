"""
Schemas de Tipo de Dispositivo
"""
from marshmallow import Schema, fields


class DeviceTypeSchema(Schema):
    """Schema para serializar tipo de dispositivo"""
    device_type_id = fields.Int(dump_only=True)
    type_name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
