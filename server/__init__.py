from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from server.routes import routes  # This is your Blueprint
from server.models import db, User

login_manager = LoginManager()

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')

    # --- App Configuration ---
    app.config['SECRET_KEY'] = 'your-secret-key'  # Use env variable in production
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'  # Change to PostgreSQL in production
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB file upload max

    # --- Initialize Extensions ---
    db.init_app(app)
    Migrate(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    # --- User Loader ---
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- Register Blueprints ---
    app.register_blueprint(routes)

    return app
