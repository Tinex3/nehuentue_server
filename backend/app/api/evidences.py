"""
API de Evidencias
"""
import os
from flask import request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import api_bp
from ..models import Evidence, Device
from ..schemas import EvidenceSchema


@api_bp.route('/evidences', methods=['GET'])
@jwt_required()
def get_evidences():
    """Listar evidencias del usuario"""
    current_user_id = get_jwt_identity()
    
    # Filtros opcionales
    zone_id = request.args.get('zone_id', type=int)
    device_id = request.args.get('device_id', type=int)
    event_id = request.args.get('event_id', type=int)
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # Obtener IDs de dispositivos del usuario
    user_device_ids = [d.device_id for d in Device.query.filter_by(user_id=current_user_id).all()]
    
    if not user_device_ids:
        return jsonify({'evidences': [], 'total': 0})
    
    query = Evidence.query.filter(Evidence.device_id.in_(user_device_ids))
    
    if zone_id:
        query = query.filter_by(zone_id=zone_id)
    if device_id:
        query = query.filter_by(device_id=device_id)
    if event_id:
        query = query.filter_by(event_id=event_id)
    
    total = query.count()
    evidences = query.order_by(Evidence.created_at.desc()).offset(offset).limit(limit).all()
    
    return jsonify({
        'evidences': [e.to_dict() for e in evidences],
        'total': total,
        'limit': limit,
        'offset': offset
    })


@api_bp.route('/evidences/<int:evidence_id>', methods=['GET'])
@jwt_required()
def get_evidence(evidence_id):
    """Obtener evidencia por ID"""
    current_user_id = get_jwt_identity()
    
    # Obtener IDs de dispositivos del usuario
    user_device_ids = [d.device_id for d in Device.query.filter_by(user_id=current_user_id).all()]
    
    evidence = Evidence.query.filter(
        Evidence.evidence_id == evidence_id,
        Evidence.device_id.in_(user_device_ids)
    ).first()
    
    if not evidence:
        return jsonify({'error': 'Evidencia no encontrada'}), 404
    
    return jsonify(evidence.to_dict())


@api_bp.route('/evidences/<int:evidence_id>/file', methods=['GET'])
@jwt_required()
def download_evidence_file(evidence_id):
    """Descargar archivo de evidencia"""
    current_user_id = get_jwt_identity()
    
    # Obtener IDs de dispositivos del usuario
    user_device_ids = [d.device_id for d in Device.query.filter_by(user_id=current_user_id).all()]
    
    evidence = Evidence.query.filter(
        Evidence.evidence_id == evidence_id,
        Evidence.device_id.in_(user_device_ids)
    ).first()
    
    if not evidence:
        return jsonify({'error': 'Evidencia no encontrada'}), 404
    
    # Construir ruta completa
    evidences_path = current_app.config.get('EVIDENCES_PATH', '/app/evidences')
    file_path = os.path.join(evidences_path, evidence.file_path)
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'Archivo no encontrado'}), 404
    
    # Determinar tipo MIME
    ext = os.path.splitext(evidence.file_path)[1].lower()
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.mp4': 'video/mp4',
        '.avi': 'video/x-msvideo',
        '.webm': 'video/webm'
    }
    mime_type = mime_types.get(ext, 'application/octet-stream')
    
    return send_file(file_path, mimetype=mime_type)


@api_bp.route('/evidences/<int:evidence_id>/ai', methods=['GET'])
@jwt_required()
def get_evidence_ai_result(evidence_id):
    """Obtener resultado de IA para una evidencia"""
    current_user_id = get_jwt_identity()
    
    # Obtener IDs de dispositivos del usuario
    user_device_ids = [d.device_id for d in Device.query.filter_by(user_id=current_user_id).all()]
    
    evidence = Evidence.query.filter(
        Evidence.evidence_id == evidence_id,
        Evidence.device_id.in_(user_device_ids)
    ).first()
    
    if not evidence:
        return jsonify({'error': 'Evidencia no encontrada'}), 404
    
    return jsonify({
        'evidence_id': evidence_id,
        'ai_metadata': evidence.ai_metadata,
        'processed': evidence.ai_metadata is not None
    })
