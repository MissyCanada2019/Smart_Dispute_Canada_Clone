# utils/email_utils.py

from flask_mail import Message
from src.app import mail  # Or wherever your Flask app instance is defined

def send_email(subject, recipient, body):
    try:
        msg = Message(subject=subject, recipients=[recipient], body=body)
        mail.send(msg)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Email failed: {e}")
