"""
Schemas de Dispositivo
"""
from marshmallow import Schema, fields, validate


class DeviceSchema(Schema):
    """Schema para serializar dispositivo"""
    device_id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    device_type_id = fields.Int(allow_none=True)
    device_type = fields.Str(dump_only=True)
    zone_id = fields.Int(allow_none=True)
    zone_name = fields.Str(dump_only=True)
    user_id = fields.Int(dump_only=True)
    status = fields.Bool()
    params = fields.Dict(allow_none=True)
    created_at = fields.DateTime(dump_only=True)


class DeviceCreateSchema(Schema):
    """Schema para crear dispositivo"""
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100)
    )
    description = fields.Str(allow_none=True, validate=validate.Length(max=500))
    device_type_id = fields.Int(required=True)
    zone_id = fields.Int(allow_none=True)
    params = fields.Dict(allow_none=True, load_default={})


class DeviceUpdateSchema(Schema):
    """Schema para actualizar dispositivo"""
    name = fields.Str(validate=validate.Length(min=1, max=100))
    description = fields.Str(allow_none=True, validate=validate.Length(max=500))
    device_type_id = fields.Int()
    zone_id = fields.Int(allow_none=True)
    status = fields.Bool()
    params = fields.Dict(allow_none=True)
