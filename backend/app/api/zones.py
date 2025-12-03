"""
API de Zonas
"""
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from . import api_bp
from ..extensions import db
from ..models import Zone
from ..schemas import ZoneSchema, ZoneCreateSchema


@api_bp.route('/zones', methods=['GET'])
@jwt_required()
def get_zones():
    """Listar zonas del usuario"""
    current_user_id = get_jwt_identity()
    
    zones = Zone.query.filter_by(user_id=current_user_id).order_by(Zone.name).all()
    
    return jsonify({
        'zones': [z.to_dict() for z in zones],
        'total': len(zones)
    })


@api_bp.route('/zones/<int:zone_id>', methods=['GET'])
@jwt_required()
def get_zone(zone_id):
    """Obtener zona por ID"""
    current_user_id = get_jwt_identity()
    
    zone = Zone.query.filter_by(zone_id=zone_id, user_id=current_user_id).first()
    
    if not zone:
        return jsonify({'error': 'Zona no encontrada'}), 404
    
    include_devices = request.args.get('include_devices', 'false').lower() == 'true'
    
    return jsonify(zone.to_dict(include_devices=include_devices))


@api_bp.route('/zones', methods=['POST'])
@jwt_required()
def create_zone():
    """Crear nueva zona"""
    current_user_id = get_jwt_identity()
    schema = ZoneCreateSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Datos inválidos', 'details': err.messages}), 400
    
    # Verificar nombre único para el usuario
    existing = Zone.query.filter_by(user_id=current_user_id, name=data['name']).first()
    if existing:
        return jsonify({'error': 'Ya existe una zona con ese nombre'}), 409
    
    zone = Zone(
        user_id=current_user_id,
        name=data['name'],
        description=data.get('description')
    )
    
    db.session.add(zone)
    db.session.commit()
    
    return jsonify({
        'message': 'Zona creada exitosamente',
        'zone': zone.to_dict()
    }), 201


@api_bp.route('/zones/<int:zone_id>', methods=['PUT'])
@jwt_required()
def update_zone(zone_id):
    """Actualizar zona"""
    current_user_id = get_jwt_identity()
    
    zone = Zone.query.filter_by(zone_id=zone_id, user_id=current_user_id).first()
    
    if not zone:
        return jsonify({'error': 'Zona no encontrada'}), 404
    
    schema = ZoneCreateSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Datos inválidos', 'details': err.messages}), 400
    
    # Verificar nombre único (si cambió)
    if data['name'] != zone.name:
        existing = Zone.query.filter_by(user_id=current_user_id, name=data['name']).first()
        if existing:
            return jsonify({'error': 'Ya existe una zona con ese nombre'}), 409
    
    zone.name = data['name']
    zone.description = data.get('description')
    
    db.session.commit()
    
    return jsonify({
        'message': 'Zona actualizada',
        'zone': zone.to_dict()
    })


@api_bp.route('/zones/<int:zone_id>', methods=['DELETE'])
@jwt_required()
def delete_zone(zone_id):
    """Eliminar zona"""
    current_user_id = get_jwt_identity()
    
    zone = Zone.query.filter_by(zone_id=zone_id, user_id=current_user_id).first()
    
    if not zone:
        return jsonify({'error': 'Zona no encontrada'}), 404
    
    db.session.delete(zone)
    db.session.commit()
    
    return jsonify({'message': 'Zona eliminada'})
