from flask.cli import FlaskGroup
from src.server import create_app
from src.server.extensions import db
from flask_migrate import Migrate, upgrade

app = create_app()
migrate = Migrate(app, db)

cli = FlaskGroup(app)

if __name__ == "__main__":
    cli()
