from flask import Flask
from src.server.extensions import db, login_manager

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")  # or your actual config

    db.init_app(app)
    login_manager.init_app(app)

    # register blueprints, etc.

    return app
