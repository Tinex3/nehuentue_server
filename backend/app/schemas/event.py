"""
Schemas de Evento
"""
from marshmallow import Schema, fields


class EventSchema(Schema):
    """Schema para serializar evento"""
    event_id = fields.Int(dump_only=True)
    device_id = fields.Int(required=True)
    device_name = fields.Str(dump_only=True)
    zone_id = fields.Int(allow_none=True)
    zone_name = fields.Str(dump_only=True)
    event_type = fields.Str(required=True)
    payload = fields.Dict(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    evidence_count = fields.Int(dump_only=True)
    evidences = fields.List(fields.Nested('EvidenceSchema'), dump_only=True)
