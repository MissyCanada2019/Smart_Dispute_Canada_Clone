from flask_sqlalchemy import SQLAlchemy
import requests

# Initialize database
db = SQLAlchemy()

# Setup Mailgun session
mailgun = requests.Session()
mailgun.auth = ("api", "your-mailgun-api-key")  # Replace with your real Mailgun key
MAILGUN_DOMAIN = "your-mailgun-domain.com"      # Replace with your Mailgun domain

def send_mailgun_email(to, subject, text):
    return mailgun.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
        data={
            "from": f"SmartDispute <mailgun@{MAILGUN_DOMAIN}>",
            "to": to,
            "subject": subject,
            "text": text
        }
    )
