from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # Secret key for sessions & security
    app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY", "dev_key")

    # Database config
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///smartdispute.db")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Large file upload limit (100MB+ if needed)
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    from server.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register routes
    from server.routes import register_routes
    register_routes(app)

    return app
