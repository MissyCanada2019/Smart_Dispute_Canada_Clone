from flask import Flask
from flask_login import LoginManager
from src.server.extensions import db, login_manager
from src.server.routes import main  # Main routes (user, upload, admin)
from src.server.auth_routes import auth  # Optional: login/register blueprint

def create_app():
    app = Flask(__name__, template_folder="../../templates", static_folder="../../static")

    # Config — replace or use a config.py
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    app.register_blueprint(main)
    app.register_blueprint(auth)  # Remove if you’re not using auth.py

    return app
