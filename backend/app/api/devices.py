"""
API de Dispositivos
"""
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from . import api_bp
from ..extensions import db
from ..models import Device, Zone, DeviceType
from ..schemas import DeviceSchema, DeviceCreateSchema, DeviceUpdateSchema
from ..services.mqtt_client import publish_command


@api_bp.route('/devices', methods=['GET'])
@jwt_required()
def get_devices():
    """Listar dispositivos del usuario"""
    current_user_id = get_jwt_identity()
    
    # Filtros opcionales
    zone_id = request.args.get('zone_id', type=int)
    device_type_id = request.args.get('device_type_id', type=int)
    status = request.args.get('status')
    
    query = Device.query.filter_by(user_id=current_user_id)
    
    if zone_id:
        query = query.filter_by(zone_id=zone_id)
    if device_type_id:
        query = query.filter_by(device_type_id=device_type_id)
    if status is not None:
        query = query.filter_by(status=status.lower() == 'true')
    
    devices = query.order_by(Device.name).all()
    
    return jsonify({
        'devices': [d.to_dict() for d in devices],
        'total': len(devices)
    })


@api_bp.route('/devices/<int:device_id>', methods=['GET'])
@jwt_required()
def get_device(device_id):
    """Obtener dispositivo por ID"""
    current_user_id = get_jwt_identity()
    
    device = Device.query.filter_by(device_id=device_id, user_id=current_user_id).first()
    
    if not device:
        return jsonify({'error': 'Dispositivo no encontrado'}), 404
    
    return jsonify(device.to_dict())


@api_bp.route('/devices', methods=['POST'])
@jwt_required()
def create_device():
    """Crear nuevo dispositivo"""
    current_user_id = get_jwt_identity()
    schema = DeviceCreateSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Datos inválidos', 'details': err.messages}), 400
    
    # Verificar nombre único para el usuario
    existing = Device.query.filter_by(user_id=current_user_id, name=data['name']).first()
    if existing:
        return jsonify({'error': 'Ya existe un dispositivo con ese nombre'}), 409
    
    # Verificar tipo de dispositivo
    device_type = DeviceType.query.get(data['device_type_id'])
    if not device_type:
        return jsonify({'error': 'Tipo de dispositivo no válido'}), 400
    
    # Verificar zona (si se proporciona)
    if data.get('zone_id'):
        zone = Zone.query.filter_by(zone_id=data['zone_id'], user_id=current_user_id).first()
        if not zone:
            return jsonify({'error': 'Zona no válida'}), 400
    
    device = Device(
        user_id=current_user_id,
        name=data['name'],
        description=data.get('description'),
        device_type_id=data['device_type_id'],
        zone_id=data.get('zone_id'),
        params=data.get('params', {})
    )
    
    db.session.add(device)
    db.session.commit()
    
    return jsonify({
        'message': 'Dispositivo creado exitosamente',
        'device': device.to_dict()
    }), 201


@api_bp.route('/devices/<int:device_id>', methods=['PUT'])
@jwt_required()
def update_device(device_id):
    """Actualizar dispositivo"""
    current_user_id = get_jwt_identity()
    
    device = Device.query.filter_by(device_id=device_id, user_id=current_user_id).first()
    
    if not device:
        return jsonify({'error': 'Dispositivo no encontrado'}), 404
    
    schema = DeviceUpdateSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Datos inválidos', 'details': err.messages}), 400
    
    # Verificar nombre único (si cambió)
    if 'name' in data and data['name'] != device.name:
        existing = Device.query.filter_by(user_id=current_user_id, name=data['name']).first()
        if existing:
            return jsonify({'error': 'Ya existe un dispositivo con ese nombre'}), 409
        device.name = data['name']
    
    # Verificar zona (si se proporciona)
    if 'zone_id' in data:
        if data['zone_id']:
            zone = Zone.query.filter_by(zone_id=data['zone_id'], user_id=current_user_id).first()
            if not zone:
                return jsonify({'error': 'Zona no válida'}), 400
        device.zone_id = data['zone_id']
    
    # Actualizar otros campos
    if 'description' in data:
        device.description = data['description']
    if 'device_type_id' in data:
        device.device_type_id = data['device_type_id']
    if 'status' in data:
        device.status = data['status']
    if 'params' in data:
        device.params = data['params']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Dispositivo actualizado',
        'device': device.to_dict()
    })


@api_bp.route('/devices/<int:device_id>', methods=['DELETE'])
@jwt_required()
def delete_device(device_id):
    """Eliminar dispositivo"""
    current_user_id = get_jwt_identity()
    
    device = Device.query.filter_by(device_id=device_id, user_id=current_user_id).first()
    
    if not device:
        return jsonify({'error': 'Dispositivo no encontrado'}), 404
    
    db.session.delete(device)
    db.session.commit()
    
    return jsonify({'message': 'Dispositivo eliminado'})


@api_bp.route('/devices/<int:device_id>/command', methods=['POST'])
@jwt_required()
def send_device_command(device_id):
    """Enviar comando a dispositivo vía MQTT"""
    current_user_id = get_jwt_identity()
    
    device = Device.query.filter_by(device_id=device_id, user_id=current_user_id).first()
    
    if not device:
        return jsonify({'error': 'Dispositivo no encontrado'}), 404
    
    data = request.json
    command = data.get('command')
    payload = data.get('payload', {})
    
    if not command:
        return jsonify({'error': 'Comando requerido'}), 400
    
    # Determinar tópico según tipo de dispositivo
    device_type_name = device.device_type.type_name if device.device_type else 'device'
    topic = f"commands/{device_type_name}s/{device_id}"
    
    message = {
        'command': command,
        'device_id': device_id,
        'payload': payload
    }
    
    try:
        publish_command(topic, message)
        return jsonify({
            'message': 'Comando enviado',
            'topic': topic,
            'command': command
        })
    except Exception as e:
        return jsonify({'error': f'Error al enviar comando: {str(e)}'}), 500
