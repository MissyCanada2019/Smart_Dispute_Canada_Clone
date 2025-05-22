# src/services/user_service.py

from werkzeug.security import generate_password_hash
from src.models import db, User
from services.mail_service import send_email

def register_user(email, password, first_name=None, last_name=None):
    if User.query.filter_by(email=email).first():
        raise ValueError("Email already registered")

    hashed_pw = generate_password_hash(password)
    user = User(email=email, password=hashed_pw,
                first_name=first_name, last_name=last_name)

    db.session.add(user)
    db.session.commit()

    # Send welcome email
    send_email(
        to=email,
        subject="Welcome to Justice Bot!",
        text="You're in! Thanks for registering with Justice Bot. Let's make the law work for you."
    )

    return user
