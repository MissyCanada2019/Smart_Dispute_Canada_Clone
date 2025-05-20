from flask.cli import FlaskGroup
from src.server import create_app
from src.server.extensions import db
from flask_migrate import Migrate, upgrade, init, migrate
import click

app = create_app()
cli = FlaskGroup(app)
migrate = Migrate(app, db)

# Optional: expose db commands
@cli.command("db")
def db_commands():
    """Run migrations."""
    click.echo("Use 'flask db migrate' or 'flask db upgrade' directly.")

if __name__ == "__main__":
    cli()
