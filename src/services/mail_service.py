import requests
import os

MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
FROM_EMAIL = os.getenv("MAILGUN_FROM_EMAIL")

def send_email(to, subject, text, html=None):
    data = {
        "from": FROM_EMAIL,
        "to": to,
        "subject": subject,
        "text": text
    }
    if html:
        data["html"] = html

    response = requests.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
        auth=("api", MAILGUN_API_KEY),
        data=data
    )
    return response
