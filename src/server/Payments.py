import os
import requests
from datetime import datetime
from src.server.extensions import db
from src.models import Payment, Case

def verify_paypal_payment(payment_id, expected_amount):
    try:
        client_id = os.getenv("PAYPAL_CLIENT_ID")
        secret = os.getenv("PAYPAL_SECRET")

        # Get OAuth token
        auth_response = requests.post(
            "https://api-m.paypal.com/v1/oauth2/token",
            auth=(client_id, secret),
            headers={"Accept": "application/json"},
            data={"grant_type": "client_credentials"},
        )

        access_token = auth_response.json().get("access_token")
        if not access_token:
            return "failed"

        # Check payment capture status
        payment_response = requests.get(
            f"https://api-m.paypal.com/v2/payments/captures/{payment_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        data = payment_response.json()

        if data.get("status") == "COMPLETED":
            paid = float(data["amount"]["value"])
            currency = data["amount"]["currency_code"]
            if currency != "CAD" or abs(paid - float(expected_amount)) > 0.01:
                return "mismatch"
            return "completed"
        return "pending"
    except Exception as e:
        print("PayPal verification error:", e)
        return "failed"
