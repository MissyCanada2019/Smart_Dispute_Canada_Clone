# src/server/extensions.py

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
csrf = CSRFProtect()

- The SmartDispute Team
"""

    try:
        return mailgun.post(
            f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
            data={
                "from": MAILGUN_FROM,
                "to": email,
                "subject": subject,
                "text": body
            }
        )
    except Exception as e:
        print(f"Mailgun error: {e}")
        return None
