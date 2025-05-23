import os
import requests
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect

# Initialize extensions
csrf = CSRFProtect()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"

# Mailgun configuration
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
MAILGUN_FROM = f"SmartDispute <mailgun@{MAILGUN_DOMAIN}>" if MAILGUN_DOMAIN else None

# Setup Mailgun session
mailgun = requests.Session()
if MAILGUN_API_KEY:
    mailgun.auth = ("api", MAILGUN_API_KEY)

def send_receipt(email, case_title, method):
    if not MAILGUN_API_KEY or not MAILGUN_DOMAIN:
        print("Mailgun is not properly configured. Email not sent.")
        return None

    subject = f"Payment Confirmation for '{case_title}'"
    body = f"""Hello,

Thank you for your payment via {method}.
Your legal package for '{case_title}' is now unlocked and available to download.

You can log in anytime to your dashboard to access your case file.

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
