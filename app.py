from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import datetime
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Secret key for session security
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "dev-secret-key")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Login manager setup
    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.init_app(app)

    from .server.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register routes
    from .server.routes import register_routes
    from .server.admin_routes import register_admin_routes
    app = register_routes(app)
    app = register_admin_routes(app)

    # Pass `now` to all templates
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow}

    return app
