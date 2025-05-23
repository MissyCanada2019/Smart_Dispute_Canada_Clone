import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

from src.server.extensions import db, login_manager

csrf = CSRFProtect()

def create_app():
    app = Flask(__name__, template_folder="../../templates", static_folder="../../static")

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///../instance/app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    Migrate(app, db)
    csrf.init_app(app)

    # Register Blueprints (import *after* app & db are initialized)
    from src.server.routes import main
    from src.server.auth_routes import auth
    from src.server.admin_cases import admin_bp
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(admin_bp)

    # Safe shell context with delayed imports
    @app.shell_context_processor
    def make_shell_context():
        from src.models import User, Case, Evidence, Payment, LegalReference, FormTemplate
        return {
            "db": db,
            "User": User,
            "Case": Case,
            "Evidence": Evidence,
            "Payment": Payment,
            "LegalReference": LegalReference,
            "FormTemplate": FormTemplate
        }

    return app
