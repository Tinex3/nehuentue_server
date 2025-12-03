"""
API de Tipos de Dispositivo
"""
from flask import jsonify
from flask_jwt_extended import jwt_required

from . import api_bp
from ..models import DeviceType
from ..schemas import DeviceTypeSchema


@api_bp.route('/device-types', methods=['GET'])
@jwt_required()
def get_device_types():
    """Listar tipos de dispositivo"""
    device_types = DeviceType.query.order_by(DeviceType.type_name).all()
    
    return jsonify({
        'device_types': DeviceTypeSchema(many=True).dump(device_types),
        'total': len(device_types)
    })


@api_bp.route('/device-types/<int:device_type_id>', methods=['GET'])
@jwt_required()
def get_device_type(device_type_id):
    """Obtener tipo de dispositivo por ID"""
    device_type = DeviceType.query.get(device_type_id)
    
    if not device_type:
        return jsonify({'error': 'Tipo de dispositivo no encontrado'}), 404
    
    return jsonify(DeviceTypeSchema().dump(device_type))
