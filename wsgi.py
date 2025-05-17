import sys
import os

# Add 'src' to system path so we can import create_app properly
sys.path.append(os.path.abspath('src'))

from server import create_app
from server.extensions import db  # ensure this exists and has db & login_manager

# Create the Flask app using the factory
application = create_app()
app = application

# OPTIONAL: Temporary block to initialize your PostgreSQL tables (ONLY RUN ONCE)
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("PostgreSQL tables created.")
