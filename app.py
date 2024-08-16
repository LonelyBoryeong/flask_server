from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from extensions import db
# SQLAlchemy 객체 생성
# Flask-Migrate 객체 생성
migrate = Migrate()
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///naver_news.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    import main_views
    app.register_blueprint(main_views.bp)
    # Initialize extensions
    db.init_app(app)
    with app.app_context():
        db.create_all()  # 테이블 생성
    migrate.init_app(app,db)
    return app