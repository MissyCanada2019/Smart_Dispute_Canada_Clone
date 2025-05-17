import sys
import os

# Add 'src' to system path so we can import the server package
sys.path.append(os.path.abspath('src'))

from server import create_app
from server.extensions import db

# Create the Flask app using your application factory
app = create_app()

# Create missing PostgreSQL tables like "user"
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("PostgreSQL tables created.")
