"""
Schemas de Medición
"""
from marshmallow import Schema, fields, validate


class MeasurementSchema(Schema):
    """Schema para serializar medición"""
    measurement_id = fields.Int(dump_only=True)
    device_id = fields.Int(required=True)
    device_name = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    recorded_at = fields.DateTime(required=True)
    data = fields.Dict(required=True)


class MeasurementCreateSchema(Schema):
    """Schema para crear medición"""
    device_id = fields.Int(required=True)
    recorded_at = fields.DateTime(required=True)
    data = fields.Dict(required=True)
