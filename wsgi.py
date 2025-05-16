import sys
import os

# Add 'src' to the system path so server/ is discoverable
sys.path.append(os.path.abspath('src'))

from server import create_app
from server.extensions import db  # update this path if your db lives somewhere else

# Create the Flask application using factory
application = create_app()
app = application

# TEMPORARY: Delete and recreate database
if os.path.exists('users.db'):
    os.remove('users.db')

with app.app_context():
    db.create_all()
