from werkzeug.security import generate_password_hash
from src.models.user import User
from src.server.extensions import db
from services.mail_service import send_email
from flask import url_for

def register_user(email, password, full_name=None):
    if User.query.filter_by(email=email).first():
        raise ValueError("Email already registered")

    hashed_pw = generate_password_hash(password)
    user = User(email=email, password_hash=hashed_pw, full_name=full_name)

    db.session.add(user)
    db.session.commit()

    token = user.generate_confirmation_token()
    confirm_url = url_for('auth.confirm_email', token=token, _external=True)

    send_email(
        to=email,
        subject="Confirm Your Email",
        text=f"Click the link to confirm your account: {confirm_url}"
    )

    return user
