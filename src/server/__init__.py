import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

from src.server.extensions import db, login_manager, csrf
from src.routes.main_routes import main as main_bp
from src.routes.auth_routes import auth_bp
from src.routes.admin_cases import admin_bp
from src.server.doc_routes import doc_bp
from src.server.login_setup import load_user  # your login loader

def create_app():
    # Get the absolute path to the directory containing this file
    src_dir = os.path.abspath(os.path.dirname(__file__))
    # Construct the absolute path to the templates directory
    templates_dir = os.path.join(src_dir, '..', 'templates')
    static_dir = os.path.join(src_dir, '..', 'static')

    app = Flask(__name__, template_folder=templates_dir, static_folder=static_dir)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///../instance/app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.user_loader(load_user)
    csrf.init_app(app)
    Migrate(app, db)

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(doc_bp)

    @app.shell_context_processor
    def make_shell_context():
        from src.models import User, Case, Evidence, Payment, LegalReference, FormTemplate
        return dict(
            db=db,
            User=User,
            Case=Case,
            Evidence=Evidence,
            Payment=Payment,
            LegalReference=LegalReference,
            FormTemplate=FormTemplate
        )

    return app
