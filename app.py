import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

def create_app():
    app = Flask(__name__)

    # Core config
    app.secret_key = os.getenv("SECRET_KEY", "super-default-key")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///site.db")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Mail config
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'smartdisputecanada@gmail.com'
    app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_APP_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = 'smartdisputecanada@gmail.com'

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Register routes
    from src.server.routes import register_routes
    register_routes(app)

    return app
