from flask_sqlalchemy import SQLAlchemy
import requests

# Initialize the database
db = SQLAlchemy()

# Configure Mailgun
MAILGUN_API_KEY = "your-mailgun-api-key"  # REPLACE THIS
MAILGUN_DOMAIN = "your-mailgun-domain.com"  # REPLACE THIS
MAILGUN_FROM_EMAIL = f"SmartDispute <mailgun@{MAILGUN_DOMAIN}>"

# Mailgun session
mailgun = requests.Session()
mailgun.auth = ("api", MAILGUN_API_KEY)

def send_receipt(email, case_title, method):
    subject = f"Payment Confirmation for '{case_title}'"
    body = f"""Hello,

Thank you for your payment via {method}. Your legal document package for the case '{case_title}' is now ready to download.

You can return to your dashboard at any time to manage your case.

- SmartDispute Team
"""
    return mailgun.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
        data={
            "from": MAILGUN_FROM_EMAIL,
            "to": email,
            "subject": subject,
            "text": body
        }
    )
