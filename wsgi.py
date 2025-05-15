import sys
import os

# Add 'src' to the system path so we can import app factory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from server import create_app

# Create the Flask application using the factory pattern
application = create_app()  # Used by Gunicorn/Render

# Optional: expose 'app' for local dev tools like Flask CLI
app = application
