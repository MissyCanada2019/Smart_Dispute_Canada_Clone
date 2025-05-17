import os
from flask import Flask
from datetime import datetime

from src.server.extensions import db, login_manager

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "dev-secret")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///site.db")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, "uploads")

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"

    # Import models AFTER initializing db
    from src.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register main routes
    from src.server.routes import register_routes
    app = register_routes(app)

    # Register optional routes
    try:
        from src.server.admin_routes import register_admin_routes
        app = register_admin_routes(app)
    except ImportError:
        pass

    try:
        from src.server.legal_help import legal_help_bp
        app.register_blueprint(legal_help_bp)
    except ImportError:
        pass

    # Global template variables
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    return app
