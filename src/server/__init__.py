import os  # <-- You need this!
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

from src.server.models import db, User
from src.server.routes import routes

login_manager = LoginManager()

def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))

    app = Flask(
        __name__,
        static_folder=os.path.join(base_dir, '..', 'static'),
        template_folder=os.path.join(base_dir, '..', 'templates')
    )

    # App Configuration
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "dev-key")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///db.sqlite3")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(base_dir, '..', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

    # Initialize Extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'routes.login'

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    app.register_blueprint(routes)

    # Ensure upload folder exists
    upload_path = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)

    return app
