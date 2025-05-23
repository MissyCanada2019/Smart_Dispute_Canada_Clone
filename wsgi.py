import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.abspath("src"))

# Import the app factory
from server import create_app

# Create the Flask app using the factory
application = create_app()

# Optional alias for local dev (Flask CLI)
app = application
