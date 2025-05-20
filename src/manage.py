from flask.cli import FlaskGroup
from src.server import create_app
from src.server.extensions import db
from flask_migrate import Migrate
from flask_migrate.cli import db as db_cli  # <-- Important!

app = create_app()
cli = FlaskGroup(app)
migrate = Migrate(app, db)

# Register db commands with the Flask CLI
cli.add_command(db_cli, "db")

if __name__ == "__main__":
    cli()
