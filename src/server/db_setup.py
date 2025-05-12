from utils.models import db
from app import app

# Run within app context to access app config and db
with app.app_context():
    print("Creating all database tables...")
    db.create_all()
    print("All tables created successfully.")
