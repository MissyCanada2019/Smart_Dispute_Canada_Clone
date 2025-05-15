import sys
import os

# Add 'src' to the system path so we can import app factory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from server import create_app

# This will be picked up by Gunicorn as `wsgi:application`
application = create_app()
