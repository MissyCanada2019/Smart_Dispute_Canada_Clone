import sys
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import datetime

# Fix for relative paths when deploying
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'server'))

from models import User
from server.routes import register_routes
from server.admin_routes import register_admin_routes
from server.legal_help import legal_help_bp

app = Flask(__name__)

# Config
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "dev-secret-key")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///site.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register routes
app = register_routes(app)
app = register_admin_routes(app)
app.register_blueprint(legal_help_bp)

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}
