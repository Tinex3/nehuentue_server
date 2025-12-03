"""
API de Autenticación
"""
from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)
from marshmallow import ValidationError

from . import api_bp
from ..extensions import db
from ..models import User
from ..schemas import UserSchema, UserCreateSchema, UserLoginSchema


@api_bp.route('/auth/register', methods=['POST'])
def register():
    """Registrar nuevo usuario"""
    schema = UserCreateSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Datos inválidos', 'details': err.messages}), 400
    
    # Verificar si ya existe
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'El usuario ya existe'}), 409
    
    # Crear usuario
    user = User(
        username=data['username'],
        email=data.get('email')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    # Generar tokens
    access_token = create_access_token(identity=str(user.user_id))
    refresh_token = create_refresh_token(identity=str(user.user_id))
    
    return jsonify({
        'message': 'Usuario creado exitosamente',
        'user': UserSchema().dump(user),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 201


@api_bp.route('/auth/login', methods=['POST'])
def login():
    """Iniciar sesión"""
    schema = UserLoginSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Datos inválidos', 'details': err.messages}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Credenciales inválidas'}), 401
    
    access_token = create_access_token(identity=str(user.user_id))
    refresh_token = create_refresh_token(identity=str(user.user_id))
    
    return jsonify({
        'message': 'Login exitoso',
        'user': UserSchema().dump(user),
        'access_token': access_token,
        'refresh_token': refresh_token
    })


@api_bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refrescar token de acceso"""
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    
    return jsonify({
        'access_token': access_token
    })


@api_bp.route('/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Obtener usuario actual"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    return jsonify(UserSchema().dump(user))


@api_bp.route('/auth/me', methods=['PUT'])
@jwt_required()
def update_current_user():
    """Actualizar usuario actual"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    data = request.json
    
    if 'email' in data:
        user.email = data['email']
    
    if 'password' in data and data['password']:
        user.set_password(data['password'])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Usuario actualizado',
        'user': UserSchema().dump(user)
    })
