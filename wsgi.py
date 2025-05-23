import sys
import os

# Ensure src is in path
sys.path.append(os.path.abspath("src"))

from server import create_app

application = create_app()
app = application  # optional alias for local dev
