import sys
import os

# Add the absolute path to the src directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from server import create_app

application = create_app()
app = application  # For local dev or Flask CLI
