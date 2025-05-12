from flask_mail import Message
from app import mail

def send_email(subject, recipient, body):
    msg = Message(subject=subject, recipients=[recipient], body=body)
    mail.send(msg)
