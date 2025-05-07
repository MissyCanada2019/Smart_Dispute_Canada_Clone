from server import app, db
from server.models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()

    # Optional: create initial admin user
    admin = User(
        email="admin@smartdisputecanada.com",
        password_hash=generate_password_hash("StrongPassword123"),
        full_name="Admin",
        is_admin=True,
        subscription_type="unlimited",
        province="ON"
    )

    existing = User.query.filter_by(email=admin.email).first()
    if not existing:
        db.session.add(admin)
        db.session.commit()
        print("Admin user created.")
    else:
        print("Admin already exists.")
