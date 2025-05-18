import sys
import os

# Ensure the src directory is in the Python path
sys.path.append(os.path.abspath("src"))

from server import create_app
from server.extensions import db

application = create_app()
app = application  # For compatibility with some servers expecting `app`

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("PostgreSQL tables created.")
    app.run(host="0.0.0.0", port=5000, debug=True)
