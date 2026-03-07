"""API 라우트"""
from app.routes.api import api_bp
from app.routes.board import board_bp
from app.routes.instar import instar_bp

__all__ = ['api_bp', 'board_bp', 'instar_bp']
