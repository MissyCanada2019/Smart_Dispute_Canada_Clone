import sys
import os

# Add 'src' to the system path so server/ is discoverable
sys.path.append(os.path.abspath('src'))

from server import create_app
from server.extensions import db

application = create_app()
app = application

# OPTIONAL: Only create DB tables if DB doesn't exist (safe check)
db_path = os.path.join(os.getcwd(), 'site.db')
if not os.path.exists(db_path):
    with app.app_context():
        db.create_all()
