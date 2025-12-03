"""
API de Eventos
"""
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta

from . import api_bp
from ..models import Event, Device
from ..schemas import EventSchema


@api_bp.route('/events', methods=['GET'])
@jwt_required()
def get_events():
    """Listar eventos del usuario"""
    current_user_id = get_jwt_identity()
    
    # Filtros opcionales
    zone_id = request.args.get('zone_id', type=int)
    device_id = request.args.get('device_id', type=int)
    event_type = request.args.get('event_type')
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # Filtro de fecha (últimas 24h por defecto)
    hours = request.args.get('hours', 24, type=int)
    since = datetime.utcnow() - timedelta(hours=hours)
    
    # Obtener IDs de dispositivos del usuario
    user_device_ids = [d.device_id for d in Device.query.filter_by(user_id=current_user_id).all()]
    
    if not user_device_ids:
        return jsonify({'events': [], 'total': 0})
    
    query = Event.query.filter(Event.device_id.in_(user_device_ids))
    query = query.filter(Event.created_at >= since)
    
    if zone_id:
        query = query.filter_by(zone_id=zone_id)
    if device_id:
        query = query.filter_by(device_id=device_id)
    if event_type:
        query = query.filter_by(event_type=event_type)
    
    total = query.count()
    events = query.order_by(Event.created_at.desc()).offset(offset).limit(limit).all()
    
    return jsonify({
        'events': [e.to_dict() for e in events],
        'total': total,
        'limit': limit,
        'offset': offset
    })


@api_bp.route('/events/<int:event_id>', methods=['GET'])
@jwt_required()
def get_event(event_id):
    """Obtener evento por ID con evidencias"""
    current_user_id = get_jwt_identity()
    
    # Obtener IDs de dispositivos del usuario
    user_device_ids = [d.device_id for d in Device.query.filter_by(user_id=current_user_id).all()]
    
    event = Event.query.filter(
        Event.event_id == event_id,
        Event.device_id.in_(user_device_ids)
    ).first()
    
    if not event:
        return jsonify({'error': 'Evento no encontrado'}), 404
    
    return jsonify(event.to_dict(include_evidences=True))


@api_bp.route('/events/stats', methods=['GET'])
@jwt_required()
def get_event_stats():
    """Estadísticas de eventos"""
    current_user_id = get_jwt_identity()
    
    # Filtro de fecha
    hours = request.args.get('hours', 24, type=int)
    since = datetime.utcnow() - timedelta(hours=hours)
    
    # Obtener IDs de dispositivos del usuario
    user_device_ids = [d.device_id for d in Device.query.filter_by(user_id=current_user_id).all()]
    
    if not user_device_ids:
        return jsonify({'stats': {}})
    
    from sqlalchemy import func
    from ..extensions import db
    
    # Contar por tipo de evento
    stats = db.session.query(
        Event.event_type,
        func.count(Event.event_id).label('count')
    ).filter(
        Event.device_id.in_(user_device_ids),
        Event.created_at >= since
    ).group_by(Event.event_type).all()
    
    return jsonify({
        'stats': {s.event_type: s.count for s in stats},
        'period_hours': hours
    })
