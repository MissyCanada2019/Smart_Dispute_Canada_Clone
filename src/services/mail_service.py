import os
import requests

MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
FROM_EMAIL = os.getenv("MAILGUN_FROM_EMAIL", "Justice Bot <noreply@justice-bot.com>")

def send_email(to, subject, text, html=None):
    if not all([MAILGUN_API_KEY, MAILGUN_DOMAIN, FROM_EMAIL]):
        raise RuntimeError("Mailgun environment variables are not properly set.")

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

    # Optional: log or raise on error
    if response.status_code != 200:
        raise Exception(f"Email failed: {response.status_code} - {response.text}")

    return response
