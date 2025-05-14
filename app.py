from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import datetime
import os

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'login'

app = Flask(__name__)

# Secret Key & Database
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "dev-secret-key")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///site.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager.init_app(app)

# Import User model for login
from server.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register routes
from server.routes import register_routes
from server.admin_routes import register_admin_routes
from server.legal_help import legal_help_bp  # <-- new import

app = register_routes(app)
app = register_admin_routes(app)
app.register_blueprint(legal_help_bp)       # <-- new registration

# Optional: inject `now()` for template use
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

if __name__ == "__main__":
    app.run(debug=True)
