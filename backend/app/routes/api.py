"""API 엔드포인트"""
from flask import Blueprint, jsonify

api_bp = Blueprint('api', __name__)


@api_bp.route('/health', methods=['GET'])
def health_check():
    """헬스 체크 엔드포인트"""
    return jsonify({'status': 'ok', 'message': 'API is running'})
