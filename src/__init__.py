from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

def create_app():
    from flask import Flask
    app = Flask(__name__)

    # Example config (replace with your actual config)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate = Migrate(app, db)

    # import and register blueprints/routes here if you have any
    # from .routes import main as main_blueprint
    # app.register_blueprint(main_blueprint)

    return app
