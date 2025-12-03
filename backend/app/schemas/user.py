"""
Schemas de Usuario
"""
from marshmallow import Schema, fields, validate, validates, ValidationError


class UserSchema(Schema):
    """Schema para serializar usuario"""
    user_id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(allow_none=True)
    created_at = fields.DateTime(dump_only=True)


class UserCreateSchema(Schema):
    """Schema para crear usuario"""
    username = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=50)
    )
    password = fields.Str(
        required=True,
        load_only=True,
        validate=validate.Length(min=6, max=100)
    )
    email = fields.Email(allow_none=True)
    
    @validates('username')
    def validate_username(self, value):
        if not value.isalnum():
            raise ValidationError('Username debe ser alfanumérico')


class UserLoginSchema(Schema):
    """Schema para login"""
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
