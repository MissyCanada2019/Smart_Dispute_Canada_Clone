import os
import requests

def verify_paypal_payment(payment_id, expected_amount):
    """
    Verifies a PayPal payment capture using PayPal's API.
    Returns: 'completed', 'mismatch', 'pending', or 'failed'.
    """
    try:
        client_id = os.getenv("PAYPAL_CLIENT_ID")
        secret = os.getenv("PAYPAL_SECRET")
        if not client_id or not secret:
            print("Missing PayPal credentials.")
            return "failed"

        # Get access token
        auth_response = requests.post(
            "https://api-m.paypal.com/v1/oauth2/token",
            auth=(client_id, secret),
            headers={"Accept": "application/json"},
            data={"grant_type": "client_credentials"},
        )

        if auth_response.status_code != 200:
            print("PayPal OAuth failed:", auth_response.text)
            return "failed"

        access_token = auth_response.json().get("access_token")
        if not access_token:
            print("No access token received.")
            return "failed"

        # Fetch payment details
        payment_response = requests.get(
            f"https://api-m.paypal.com/v2/payments/captures/{payment_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        if payment_response.status_code != 200:
            print("PayPal payment lookup failed:", payment_response.text)
            return "failed"

        data = payment_response.json()
        status = data.get("status")
        amount_info = data.get("amount", {})
        paid = float(amount_info.get("value", 0))
        currency = amount_info.get("currency_code", "CAD")

        if status == "COMPLETED":
            if currency != "CAD" or abs(paid - float(expected_amount)) > 0.01:
                return "mismatch"
            return "completed"
        return "pending"

    except Exception as e:
        print("PayPal verification error:", str(e))
        return "failed"
