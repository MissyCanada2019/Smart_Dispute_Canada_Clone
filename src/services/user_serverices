from werkzeug.security import generate_password_hash
from flask import url_for
from src.models import db, User
from src.services.mail_service import send_email

def register_user(email, password, full_name=None):
    if User.query.filter_by(email=email).first():
        raise ValueError("Email already registered")

    hashed_pw = generate_password_hash(password)
    user = User(
        email=email,
        password_hash=hashed_pw,
        full_name=full_name,
        is_verified=False,
        role="user"
    )

    db.session.add(user)
    db.session.commit()

    # Generate email confirmation token
    token = user.generate_confirmation_token()
    confirm_url = url_for('auth.confirm_email', token=token, _external=True)

    # Send confirmation email
    send_email(
        to=email,
        subject="Confirm Your Email - Justice Bot",
        text=f"Thanks for registering, {full_name}!\n\nClick the link to confirm your email:\n{confirm_url}"
    )

    return user
