from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import requests

# Database setup
db = SQLAlchemy()

# Login manager setup
login_manager = LoginManager()
login_manager.login_view = "auth.login"  # adjust this if your login route is named differently

# Mailgun setup
MAILGUN_API_KEY = "your-mailgun-api-key"  # << replace
MAILGUN_DOMAIN = "your-mailgun-domain.com"  # << replace
MAILGUN_FROM = f"SmartDispute <mailgun@{MAILGUN_DOMAIN}>"

mailgun = requests.Session()
mailgun.auth = ("api", MAILGUN_API_KEY)

def send_receipt(email, case_title, method):
    subject = f"Payment Confirmation for '{case_title}'"
    body = f"""Hello,

Thank you for your payment via {method}. Your legal document package for '{case_title}' is now available.

- SmartDispute Team
"""
    return mailgun.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
        data={
            "from": MAILGUN_FROM,
            "to": email,
            "subject": subject,
            "text": body
        }
    )
