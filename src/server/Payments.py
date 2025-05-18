import os
import requests
from datetime import datetime
from src.server.extensions import db
from src.models import Payment, Case

def verify_paypal_payment(payment_id, expected_amount):
    try:
        client_id = os.getenv("PAYPAL_CLIENT_ID")
        secret = os.getenv("PAYPAL_SECRET")

        # Get OAuth token from PayPal
        auth_response = requests.post(
            "https://api-m.paypal.com/v1/oauth2/token",
            auth=(client_id, secret),
            headers={"Accept": "application/json"},
            data={"grant_type": "client_credentials"},
        )

        if auth_response.status_code != 200:
            print("PayPal auth failed:", auth_response.text)
            return "failed"

        access_token = auth_response.json().get("access_token")
        if not access_token:
            print("Access token not received from PayPal")
            return "failed"

        # Check the payment capture status
        payment_response = requests.get(
            f"https://api-m.paypal.com/v2/payments/captures/{payment_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        if payment_response.status_code != 200:
            print("Payment lookup failed:", payment_response.text)
            return "failed"

        data = payment_response.json()
        status = data.get("status")
        paid_amount = float(data["amount"]["value"])
        currency = data["amount"]["currency_code"]

        if status == "COMPLETED":
            if currency != "CAD":
                print("Currency mismatch:", currency)
                return "mismatch"
            if abs(paid_amount - float(expected_amount)) > 0.01:
                print("Amount mismatch:", paid_amount)
                return "mismatch"
            return "completed"
        else:
            return "pending"

    except Exception as e:
        print("PayPal verification error:", str(e))
        return "failed"
