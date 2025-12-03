"""
Schemas de Evidencia
"""
from marshmallow import Schema, fields


class EvidenceSchema(Schema):
    """Schema para serializar evidencia"""
    evidence_id = fields.Int(dump_only=True)
    device_id = fields.Int(allow_none=True)
    zone_id = fields.Int(allow_none=True)
    event_id = fields.Int(allow_none=True)
    file_path = fields.Str(required=True)
    ai_metadata = fields.Dict(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
