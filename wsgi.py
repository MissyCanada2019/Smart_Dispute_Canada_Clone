import sys
import os

# Add 'src' to system path to allow imports from that directory
sys.path.append(os.path.abspath('src'))

from server import create_app
from server.extensions import db  # must exist and contain 'db = SQLAlchemy()'

# Create the Flask app using the application factory
app = create_app()

# Optional: Run once to create tables
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("PostgreSQL tables created.")
