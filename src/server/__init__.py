import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

from src.models import db, User
from src.server.routes import register_routes
from src.server.admin_routes import register_admin_routes

load_dotenv()

login_manager = LoginManager()
login_manager.login_view = 'login'

def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))

    app = Flask(
        __name__,
        static_folder=os.path.join(base_dir, '..', 'static'),
        template_folder=os.path.join(base_dir, 'templates')
    )

    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "default-secret-key")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///site.db")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(base_dir, '..', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

    db.init_app(app)
    Migrate(app, db)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    register_routes(app)
    register_admin_routes(app)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    return app
