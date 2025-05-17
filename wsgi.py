import sys
import os

# Add 'src' to system path
sys.path.append(os.path.abspath('src'))

from server import create_app
from server.extensions import db

application = create_app()
app = application

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("PostgreSQL tables created.")
