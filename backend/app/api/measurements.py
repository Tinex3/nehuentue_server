"""
API de Mediciones (Telemetría)
"""
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta

from . import api_bp
from ..models import Measurement, Device
from ..schemas import MeasurementSchema


@api_bp.route('/measurements', methods=['GET'])
@jwt_required()
def get_measurements():
    """Listar mediciones del usuario"""
    current_user_id = get_jwt_identity()
    
    # Filtros opcionales
    device_id = request.args.get('device_id', type=int)
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # Filtro de fecha
    hours = request.args.get('hours', 24, type=int)
    since = datetime.utcnow() - timedelta(hours=hours)
    
    # Obtener IDs de dispositivos del usuario
    user_device_ids = [d.device_id for d in Device.query.filter_by(user_id=current_user_id).all()]
    
    if not user_device_ids:
        return jsonify({'measurements': [], 'total': 0})
    
    query = Measurement.query.filter(Measurement.device_id.in_(user_device_ids))
    query = query.filter(Measurement.recorded_at >= since)
    
    if device_id:
        query = query.filter_by(device_id=device_id)
    
    total = query.count()
    measurements = query.order_by(Measurement.recorded_at.desc()).offset(offset).limit(limit).all()
    
    return jsonify({
        'measurements': [m.to_dict() for m in measurements],
        'total': total,
        'limit': limit,
        'offset': offset,
        'period_hours': hours
    })


@api_bp.route('/measurements/device/<int:device_id>', methods=['GET'])
@jwt_required()
def get_device_measurements(device_id):
    """Obtener mediciones de un dispositivo específico"""
    current_user_id = get_jwt_identity()
    
    # Verificar que el dispositivo pertenece al usuario
    device = Device.query.filter_by(device_id=device_id, user_id=current_user_id).first()
    
    if not device:
        return jsonify({'error': 'Dispositivo no encontrado'}), 404
    
    # Parámetros
    limit = request.args.get('limit', 100, type=int)
    hours = request.args.get('hours', 24, type=int)
    since = datetime.utcnow() - timedelta(hours=hours)
    
    measurements = Measurement.query.filter(
        Measurement.device_id == device_id,
        Measurement.recorded_at >= since
    ).order_by(Measurement.recorded_at.desc()).limit(limit).all()
    
    return jsonify({
        'device_id': device_id,
        'device_name': device.name,
        'measurements': [m.to_dict() for m in measurements],
        'total': len(measurements),
        'period_hours': hours
    })


@api_bp.route('/measurements/device/<int:device_id>/latest', methods=['GET'])
@jwt_required()
def get_device_latest_measurement(device_id):
    """Obtener última medición de un dispositivo"""
    current_user_id = get_jwt_identity()
    
    # Verificar que el dispositivo pertenece al usuario
    device = Device.query.filter_by(device_id=device_id, user_id=current_user_id).first()
    
    if not device:
        return jsonify({'error': 'Dispositivo no encontrado'}), 404
    
    measurement = Measurement.query.filter_by(
        device_id=device_id
    ).order_by(Measurement.recorded_at.desc()).first()
    
    if not measurement:
        return jsonify({
            'device_id': device_id,
            'device_name': device.name,
            'measurement': None
        })
    
    return jsonify({
        'device_id': device_id,
        'device_name': device.name,
        'measurement': measurement.to_dict()
    })


@api_bp.route('/measurements/summary', methods=['GET'])
@jwt_required()
def get_measurements_summary():
    """Resumen de mediciones por dispositivo"""
    current_user_id = get_jwt_identity()
    
    hours = request.args.get('hours', 24, type=int)
    since = datetime.utcnow() - timedelta(hours=hours)
    
    # Obtener dispositivos del usuario con mediciones
    devices = Device.query.filter_by(user_id=current_user_id).all()
    
    summary = []
    for device in devices:
        latest = Measurement.query.filter(
            Measurement.device_id == device.device_id,
            Measurement.recorded_at >= since
        ).order_by(Measurement.recorded_at.desc()).first()
        
        count = Measurement.query.filter(
            Measurement.device_id == device.device_id,
            Measurement.recorded_at >= since
        ).count()
        
        if count > 0:
            summary.append({
                'device_id': device.device_id,
                'device_name': device.name,
                'device_type': device.device_type.type_name if device.device_type else None,
                'measurement_count': count,
                'latest_data': latest.data if latest else None,
                'latest_recorded_at': latest.recorded_at.isoformat() if latest else None
            })
    
    return jsonify({
        'summary': summary,
        'period_hours': hours
    })
