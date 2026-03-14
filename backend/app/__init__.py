"""Flask 애플리케이션 초기화"""
from pathlib import Path

from flask import Flask, render_template

from app.config import Config

# 프로젝트 루트 (capstone/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent


def create_app(config_class=Config) -> Flask:
    """Flask 앱 팩토리"""
    template_dir = BASE_DIR / 'frontend' / 'templates'
    static_dir = BASE_DIR / 'frontend' / 'static'
    app = Flask(__name__, template_folder=str(template_dir), static_folder=str(static_dir))
    app.config.from_object(config_class)

    from app.routes import api_bp, board_bp, instar_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(board_bp)
    app.register_blueprint(instar_bp, url_prefix='/api/instar')

    @app.route('/')
    def index():
        return render_template('home_overview/home_overview_before.html')

    @app.route('/login')
    def login_page():
        return render_template('login/login.html')

    @app.route('/signup')
    def signup_page():
        return render_template('login/signup.html')

    @app.route('/home')
    def home_page():
        return render_template('home_overview/home_overview_after.html')

    @app.route('/recommend')
    def recommend_page():
        return render_template('recommend/recommend.html')

    @app.route('/intro')
    def intro_page():
        return render_template('home_overview/home_overview_before.html')

    @app.route('/dashboard')
    def dashboard_page():
        return render_template('dashboard/dashboard.html')

    @app.route('/score')
    def score_page():
        return render_template('score/score_manager.html')

    @app.route('/result')
    def result_page():
        return render_template('result.html')

    @app.route('/timetable')
    def timetable_page():
        return render_template('timetable/timetable.html')

    return app
