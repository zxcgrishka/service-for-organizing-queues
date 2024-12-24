from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .config import Config
from .models import db, User
from .routes import init_routes

# Инициализация приложения
login_manager = LoginManager()
login_manager.login_view = 'login'

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()

    init_routes(app)

    return app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
