from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
import os

# Extensions
from src.server.extensions import db, login_manager

# Blueprints
from src.routes.auth_routes import auth_bp
from src.routes.main_routes import main  # if you renamed `main.py`
from src.routes.admin_cases import admin_bp
from src.server.doc_routes import doc_bp  # <-- this was fine

csrf = CSRFProtect()

def create_app():
    app = Flask(__name__, template_folder="../../templates", static_folder="../../static")

    # Config
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///../instance/app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    Migrate(app, db)
    csrf.init_app(app)

    # Register blueprints (do this **inside** the function)
    app.register_blueprint(auth_bp)
    app.register_blueprint(main)
    app.register_blueprint(admin_bp)
    app.register_blueprint(doc_bp)  # moved inside here

    # Shell context for `flask shell`
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
