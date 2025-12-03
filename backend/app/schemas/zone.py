"""
Schemas de Zona
"""
from marshmallow import Schema, fields, validate


class ZoneSchema(Schema):
    """Schema para serializar zona"""
    zone_id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    device_count = fields.Int(dump_only=True)
    devices = fields.List(fields.Nested('DeviceSchema', exclude=['zone_id', 'zone_name']), dump_only=True)


class ZoneCreateSchema(Schema):
    """Schema para crear/actualizar zona"""
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100)
    )
    description = fields.Str(allow_none=True, validate=validate.Length(max=500))
