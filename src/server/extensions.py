from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import requests

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"

# Mailgun configuration
MAILGUN_API_KEY = "your-mailgun-api-key"  # Replace with real key
MAILGUN_DOMAIN = "your-mailgun-domain.com"  # Replace with your domain
MAILGUN_FROM = f"SmartDispute <mailgun@{MAILGUN_DOMAIN}>"

mailgun = requests.Session()
mailgun.auth = ("api", MAILGUN_API_KEY)

def send_receipt(email, case_title, method):
    subject = f"Payment Confirmation for '{case_title}'"
    body = f"""Hello,

Thank you for your payment via {method}.
Your legal package for '{case_title}' is now unlocked and available to download.

You can log in anytime to your dashboard to access your case file.

- The SmartDispute Team
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
