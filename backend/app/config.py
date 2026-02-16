"""애플리케이션 설정"""
import os
from pathlib import Path


class Config:
    """기본 설정"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', '1') == '1'

    # 프로젝트 루트 경로
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
