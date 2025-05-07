import os
import requests
import logging
import json
import uuid
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

# Enable sandbox testing mode (no real API calls)
SANDBOX_MODE = True

# PayPal API endpoints
PAYPAL_API_BASE_SANDBOX = "https://api-m.sandbox.paypal.com"
PAYPAL_API_BASE_PRODUCTION = "https://api-m.paypal.com"

# Cache for access token to avoid requesting it for every payment
token_cache = {
    'access_token': None,
    'expires_at': None
}

# Initialize with current time minus 1 day to ensure first request gets a new token
token_cache['expires_at'] = datetime.now() - timedelta(days=1)

def get_paypal_api_base():
    """Get the appropriate PayPal API base URL based on environment"""
    # Use sandbox for development, production for... well, production
    if os.environ.get('FLASK_ENV') == 'production':
        return PAYPAL_API_BASE_PRODUCTION
    return PAYPAL_API_BASE_SANDBOX

def get_paypal_access_token():
    """
    Get a PayPal access token using client credentials
    
    Returns:
        str: Access token or None if error
    """
    # Check if we have a valid cached token
    if token_cache['access_token'] and token_cache['expires_at'] and datetime.now() < token_cache['expires_at']:
        return token_cache['access_token']
    
    # Get credentials from environment
    client_id = os.environ.get('PAYPAL_CLIENT_ID')
    client_secret = os.environ.get('PAYPAL_CLIENT_SECRET')
    
    # Add debug logging
    print(f"DEBUG: Client ID exists: {bool(client_id)}, Secret exists: {bool(client_secret)}")
    
    if not client_id or not client_secret:
        logger.error("PayPal client credentials not set in environment variables")
        return None
    
    try:
        # Endpoint for token request
        url = f"{get_paypal_api_base()}/v1/oauth2/token"
        print(f"DEBUG: Token URL: {url}")
        
        # Headers and data for the request
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "client_credentials"
        }
        
        # Make the request with Basic Auth (client ID and secret)
        print(f"DEBUG: Making token request with headers: {headers}")
        response = requests.post(
            url,
            auth=(client_id, client_secret),
            headers=headers,
            data=data
        )
        
        if response.status_code == 200:
            # Parse response and cache the token
            token_data = response.json()
            token_cache['access_token'] = token_data['access_token']
            # Set expiry time slightly before actual expiry to be safe
            expires_in_seconds = token_data['expires_in'] - 60  # Subtract 60 seconds for safety
            token_cache['expires_at'] = datetime.now() + timedelta(seconds=expires_in_seconds)
            return token_cache['access_token']
        else:
            print(f"DEBUG: Token response: {response.status_code} - {response.text}")
            logger.error(f"Failed to get PayPal access token: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Exception getting PayPal access token: {str(e)}")
        return None

def create_paypal_order(amount, currency='CAD', description='SmartDispute.ai Document Fee'):
    """
    Create a PayPal order for a payment
    
    Args:
        amount (float): Amount to charge
        currency (str): Currency code (default: CAD)
        description (str): Description of the payment
        
    Returns:
        dict: Order details or None if error
    """
    # Use sandbox mode if enabled
    if SANDBOX_MODE:
        return create_sandbox_paypal_order(amount, currency, description)
    
    # Get access token
    access_token = get_paypal_access_token()
    if not access_token:
        return None
    
    try:
        # Endpoint for creating an order
        url = f"{get_paypal_api_base()}/v2/checkout/orders"
        
        # Headers for the request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        # Order data
        order_data = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": currency,
                        "value": str(amount)  # PayPal expects a string
                    },
                    "description": description
                }
            ],
            "application_context": {
                "return_url": "https://smartdispute.ai/payment/success",
                "cancel_url": "https://smartdispute.ai/payment/cancel"
            }
        }
        
        # Make the request
        response = requests.post(
            url,
            headers=headers,
            json=order_data
        )
        
        if response.status_code in (200, 201):
            return response.json()
        else:
            logger.error(f"Failed to create PayPal order: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Exception creating PayPal order: {str(e)}")
        return None
        
def create_sandbox_paypal_order(amount, currency='CAD', description='SmartDispute.ai Document Fee'):
    """
    Create a simulated PayPal order for testing
    
    Args:
        amount (float): Amount to charge
        currency (str): Currency code (default: CAD)
        description (str): Description of the payment
        
    Returns:
        dict: Simulated order details
    """
    # Generate a unique order ID
    order_id = f"SANDBOX-{uuid.uuid4().hex[:8]}"
    
    # Create a simulated order response similar to PayPal's format
    return {
        "id": order_id,
        "status": "CREATED",
        "links": [
            {
                "href": f"https://sandbox.paypal.com/checkoutnow?token={order_id}",
                "rel": "approve",
                "method": "GET"
            },
            {
                "href": f"https://api.sandbox.paypal.com/v2/checkout/orders/{order_id}",
                "rel": "self",
                "method": "GET"
            },
            {
                "href": f"https://api.sandbox.paypal.com/v2/checkout/orders/{order_id}/capture",
                "rel": "capture",
                "method": "POST"
            }
        ],
        "purchase_units": [
            {
                "reference_id": f"PURCH-{uuid.uuid4().hex[:6]}",
                "amount": {
                    "currency_code": currency,
                    "value": str(amount)
                },
                "description": description
            }
        ],
        "create_time": datetime.now().isoformat() + "Z",
        "update_time": datetime.now().isoformat() + "Z"
    }

def capture_paypal_order(order_id):
    """
    Capture a PayPal order after it has been approved
    
    Args:
        order_id (str): PayPal order ID
        
    Returns:
        dict: Capture details or None if error
    """
    # Use sandbox mode if enabled
    if SANDBOX_MODE:
        return capture_sandbox_paypal_order(order_id)
    
    # Get access token
    access_token = get_paypal_access_token()
    if not access_token:
        return None
    
    try:
        # Endpoint for capturing an order
        url = f"{get_paypal_api_base()}/v2/checkout/orders/{order_id}/capture"
        
        # Headers for the request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        # Make the request
        response = requests.post(url, headers=headers)
        
        if response.status_code in (200, 201):
            capture_data = response.json()
            # Check if the capture was successful
            if capture_data['status'] == 'COMPLETED':
                return capture_data
            else:
                logger.error(f"PayPal capture not completed: {capture_data['status']}")
                return None
        else:
            logger.error(f"Failed to capture PayPal order: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Exception capturing PayPal order: {str(e)}")
        return None
        
def capture_sandbox_paypal_order(order_id):
    """
    Capture a simulated PayPal order for testing
    
    Args:
        order_id (str): PayPal order ID (from create_sandbox_paypal_order)
        
    Returns:
        dict: Simulated capture details
    """
    # Extract amount from order_id (in a real scenario we would lookup the actual order)
    # For testing, we'll just simulate a capture with a standard amount
    capture_id = f"CAPTURE-{uuid.uuid4().hex[:8]}"
    
    # Create a simulated capture response similar to PayPal's format
    return {
        "id": order_id,
        "status": "COMPLETED",
        "purchase_units": [
            {
                "reference_id": f"PURCH-{uuid.uuid4().hex[:6]}",
                "payments": {
                    "captures": [
                        {
                            "id": capture_id,
                            "status": "COMPLETED",
                            "amount": {
                                "currency_code": "CAD",
                                "value": "9.99"  # Default test amount
                            },
                            "final_capture": True,
                            "create_time": datetime.now().isoformat() + "Z",
                            "update_time": datetime.now().isoformat() + "Z"
                        }
                    ]
                }
            }
        ],
        "payer": {
            "name": {
                "given_name": "Test",
                "surname": "User"
            },
            "email_address": "test-buyer@example.com",
            "payer_id": f"TESTPAYER{uuid.uuid4().hex[:6]}"
        },
        "create_time": datetime.now().isoformat() + "Z",
        "update_time": datetime.now().isoformat() + "Z"
    }

def process_paypal_payment(order_id, expected_amount=None):
    """
    Process a PayPal payment by capturing an approved order
    
    Args:
        order_id (str): PayPal order ID
        expected_amount (float, optional): Expected payment amount for verification
        
    Returns:
        str: Payment status ('completed', 'pending', 'failed')
    """
    # Capture the order
    capture_data = capture_paypal_order(order_id)
    
    if not capture_data:
        return 'failed'
    
    # Check capture status
    if capture_data['status'] != 'COMPLETED':
        return 'pending'
    
    # Verify payment amount if expected amount is provided
    if expected_amount is not None:
        # Get the actual captured amount
        try:
            captured_amount = float(capture_data['purchase_units'][0]['payments']['captures'][0]['amount']['value'])
            if abs(captured_amount - expected_amount) > 0.01:  # Allow for small rounding differences
                logger.error(f"Payment amount mismatch: expected {expected_amount}, got {captured_amount}")
                return 'failed'
        except (KeyError, ValueError) as e:
            logger.error(f"Error verifying payment amount: {str(e)}")
            return 'failed'
    
    return 'completed'

def get_paypal_payment_details(capture_id):
    """
    Get details of a PayPal payment capture
    
    Args:
        capture_id (str): PayPal capture ID
        
    Returns:
        dict: Payment details or None if error
    """
    # Use sandbox mode if enabled
    if SANDBOX_MODE:
        return get_sandbox_payment_details(capture_id)
    
    # Get access token
    access_token = get_paypal_access_token()
    if not access_token:
        return None
    
    try:
        # Endpoint for getting capture details
        url = f"{get_paypal_api_base()}/v2/payments/captures/{capture_id}"
        
        # Headers for the request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        # Make the request
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to get PayPal payment details: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Exception getting PayPal payment details: {str(e)}")
        return None
        
def get_sandbox_payment_details(capture_id):
    """
    Get simulated details of a PayPal payment capture for testing
    
    Args:
        capture_id (str): PayPal capture ID
        
    Returns:
        dict: Simulated payment details
    """
    # Create a simulated payment details response similar to PayPal's format
    return {
        "id": capture_id,
        "status": "COMPLETED",
        "amount": {
            "currency_code": "CAD",
            "value": "9.99"  # Default test amount
        },
        "final_capture": True,
        "seller_protection": {
            "status": "ELIGIBLE",
            "dispute_categories": [
                "ITEM_NOT_RECEIVED",
                "UNAUTHORIZED_TRANSACTION"
            ]
        },
        "links": [
            {
                "href": f"https://api.sandbox.paypal.com/v2/payments/captures/{capture_id}",
                "rel": "self",
                "method": "GET"
            },
            {
                "href": f"https://api.sandbox.paypal.com/v2/payments/captures/{capture_id}/refund",
                "rel": "refund",
                "method": "POST"
            }
        ],
        "create_time": datetime.now().isoformat() + "Z",
        "update_time": datetime.now().isoformat() + "Z"
    }

def refund_paypal_payment(capture_id, amount=None, reason=None):
    """
    Refund a PayPal payment
    
    Args:
        capture_id (str): PayPal capture ID
        amount (float, optional): Amount to refund (if None, full refund)
        reason (str, optional): Reason for the refund
        
    Returns:
        dict: Refund details or None if error
    """
    # Use sandbox mode if enabled
    if SANDBOX_MODE:
        return refund_sandbox_payment(capture_id, amount, reason)
    
    # Get access token
    access_token = get_paypal_access_token()
    if not access_token:
        return None
    
    try:
        # Endpoint for refunding a capture
        url = f"{get_paypal_api_base()}/v2/payments/captures/{capture_id}/refund"
        
        # Headers for the request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        # Refund data
        refund_data = {}
        
        # Add amount if partial refund
        if amount is not None:
            refund_data["amount"] = {
                "value": str(amount),
                "currency_code": "CAD"  # Assuming CAD as default currency
            }
        
        # Add note_to_payer if reason provided
        if reason:
            refund_data["note_to_payer"] = reason
        
        # Make the request
        response = requests.post(
            url,
            headers=headers,
            json=refund_data if refund_data else None
        )
        
        if response.status_code in (200, 201, 202):
            return response.json()
        else:
            logger.error(f"Failed to refund PayPal payment: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Exception refunding PayPal payment: {str(e)}")
        return None

def refund_sandbox_payment(capture_id, amount=None, reason=None):
    """
    Refund a simulated PayPal payment for testing
    
    Args:
        capture_id (str): PayPal capture ID
        amount (float, optional): Amount to refund (if None, full refund)
        reason (str, optional): Reason for the refund
        
    Returns:
        dict: Simulated refund details
    """
    refund_id = f"REFUND-{uuid.uuid4().hex[:8]}"
    refund_amount = str(amount) if amount is not None else "9.99"  # Default test amount
    
    # Create a simulated refund response similar to PayPal's format
    return {
        "id": refund_id,
        "status": "COMPLETED",
        "links": [
            {
                "href": f"https://api.sandbox.paypal.com/v2/payments/refunds/{refund_id}",
                "rel": "self",
                "method": "GET"
            }
        ],
        "amount": {
            "currency_code": "CAD",
            "value": refund_amount
        },
        "note_to_payer": reason if reason else "Refund for your purchase",
        "create_time": datetime.now().isoformat() + "Z",
        "update_time": datetime.now().isoformat() + "Z"
    }