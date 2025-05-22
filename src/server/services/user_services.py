from werkzeug.security import generate_password_hash
from flask import url_for
from src.models import db, User
from src.services.mail_service import send_email

def register_user(email, password, first_name=None, last_name=None):
    if User.query.filter_by(email=email).first():
        raise ValueError("Email already registered")

    hashed_pw = generate_password_hash(password)
    full_name = f"{first_name} {last_name}".strip() if first_name else None

    user = User(email=email, password_hash=hashed_pw, full_name=full_name)
    db.session.add(user)
    db.session.commit()

    token = user.generate_confirmation_token()
    confirm_url = url_for('auth.confirm_email', token=token, _external=True)

    send_email(
        to=email,
        subject="Confirm Your Email - Justice Bot",
        text=f"You're in! Click to confirm your email: {confirm_url}"
    )

    return user
