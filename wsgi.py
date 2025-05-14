import sys
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import datetime

# Add the parent directory of 'server' to the system path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Setup
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'login'

app = Flask(__name__)

# Config
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "dev-secret-key")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///site.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init extensions
db.init_app(app)
login_manager.init_app(app)

# Import and register
from server.models import User
from server.routes import register_routes
from server.admin_routes import register_admin_routes
from server.legal_help import legal_help_bp

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app = register_routes(app)
app = register_admin_routes(app)
app.register_blueprint(legal_help_bp)

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

# Expose app
if __name__ != "__main__":
    application = app
