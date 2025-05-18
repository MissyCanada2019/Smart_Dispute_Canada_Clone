# manage.py

from flask.cli import FlaskGroup
from src.server import create_app
from src.server.extensions import db
from flask_migrate import Migrate

# Create app and CLI group
app = create_app()
cli = FlaskGroup(app)
migrate = Migrate(app, db)

if __name__ == "__main__":
    cli()
