# manage.py

from flask.cli import FlaskGroup
from src.server import create_app
from src.server.extensions import db
from flask_migrate import MigrateCommand

app = create_app()
cli = FlaskGroup(app)

# Register Flask-Migrate commands
cli.add_command('db', MigrateCommand)

if __name__ == "__main__":
    cli()
