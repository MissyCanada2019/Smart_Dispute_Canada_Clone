from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
import os

# Extensions
from src.server.extensions import db, login_manager

# Blueprints from the correct folders
from src.routes.auth_routes import auth_bp
from src.routes.main_routes import main  # rename `main.py` to `main_routes.py` if needed
from src.routes.admin_cases import admin_bp

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

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main)
    app.register_blueprint(admin_bp)

    # Shell context
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
