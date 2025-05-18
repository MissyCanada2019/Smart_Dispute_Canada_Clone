from flask.cli import FlaskGroup
from src.server import create_app
from src.server.extensions import db
from flask_migrate import Migrate

app = create_app()
cli = FlaskGroup(app)

# Setup Flask-Migrate
migrate = Migrate(app, db)

if __name__ == "__main__":
    cli()
