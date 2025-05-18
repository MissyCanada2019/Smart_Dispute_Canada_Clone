import os
import logging
import json
import requests
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

def process_paypal_payment(payment_id, amount):
    """
    Process a PayPal payment
    
    Args:
        payment_id (str): PayPal payment ID
        amount (float): Payment amount
        
    Returns:
        str: Payment status ('completed', 'pending', 'failed')
    """
    try:
        # In a real implementation, this would verify the payment with PayPal API
        # For development purposes, we'll simulate a successful payment
        
        # Get PayPal API credentials from environment variables
        paypal_client_id = os.environ.get('PAYPAL_CLIENT_ID', '')
        paypal_secret = os.environ.get('PAYPAL_SECRET', '')
        
        if not paypal_client_id or not paypal_secret:
            logger.warning("PayPal API credentials not set. Simulating payment verification.")
            return verify_payment_dev_mode(payment_id, amount)
        
        # Verify the payment with PayPal API in production
        return verify_payment_production(payment_id, amount, paypal_client_id, paypal_secret)
    except Exception as e:
        logger.error(f"Error processing PayPal payment: {str(e)}")
        return 'failed'

def verify_payment_dev_mode(payment_id, amount):
    """
    Verify payment in development mode (simulation)
    
    Args:
        payment_id (str): PayPal payment ID
        amount (float): Payment amount
        
    Returns:
        str: Payment status ('completed', 'pending', 'failed')
    """
    logger.info(f"DEV MODE: Simulating verification of PayPal payment {payment_id} for ${amount}")
    
    # For testing, consider payments with 'fail' in the ID as failed
    if 'fail' in payment_id.lower():
        return 'failed'
    
    # Simulate checking payment amount
    if not payment_id or amount <= 0:
        return 'failed'
    
    return 'completed'

def verify_payment_production(payment_id, amount, client_id, secret):
    """
    Verify payment in production mode using PayPal API
    
    Args:
        payment_id (str): PayPal payment ID
        amount (float): Payment amount
        client_id (str): PayPal API client ID
        secret (str): PayPal API secret
        
    Returns:
        str: Payment status ('completed', 'pending', 'failed')
    """
    try:
        # Get OAuth token
        token_url = "https://api.paypal.com/v1/oauth2/token"
        token_headers = {
            "Accept": "application/json",
            "Accept-Language": "en_US"
        }
        token_data = {
            "grant_type": "client_credentials"
        }
        
        token_response = requests.post(
            token_url,
            auth=(client_id, secret),
            headers=token_headers,
            data=token_data
        )
        
        if token_response.status_code != 200:
            logger.error(f"Failed to get PayPal OAuth token: {token_response.text}")
            return 'failed'
        
        access_token = token_response.json().get('access_token')
        
        # Verify payment
        payment_url = f"https://api.paypal.com/v2/payments/captures/{payment_id}"
        payment_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        payment_response = requests.get(
            payment_url,
            headers=payment_headers
        )
        
        if payment_response.status_code != 200:
            logger.error(f"Failed to verify PayPal payment: {payment_response.text}")
            return 'failed'
        
        payment_data = payment_response.json()
        
        # Check payment status
        status = payment_data.get('status', '').lower()
        
        if status == 'completed':
            # Verify payment amount
            payment_amount = float(payment_data.get('amount', {}).get('value', 0))
            payment_currency = payment_data.get('amount', {}).get('currency_code', '')
            
            if payment_currency != 'CAD' or abs(payment_amount - float(amount)) > 0.01:
                logger.warning(f"Payment amount mismatch: expected ${amount} CAD, got ${payment_amount} {payment_currency}")
                return 'failed'
            
            return 'completed'
        elif status in ['pending', 'unclaimed']:
            return 'pending'
        else:
            return 'failed'
    
    except Exception as e:
        logger.error(f"Error verifying PayPal payment: {str(e)}")
        return 'failed'

def create_subscription(user_id, plan_type, payment_id=None):
    """
    Create or update a user's subscription
    
    Args:
        user_id (int): User ID
        plan_type (str): Subscription plan type
        payment_id (str, optional): Payment ID if applicable
        
    Returns:
        tuple: (success, message)
            - success (bool): Whether the operation was successful
            - message (str): Success or error message
    """
    try:
        from app import db
        from models import User, Payment
        
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"
        
        # Update user subscription
        user.subscription_type = plan_type
        
        # Set subscription end date based on plan type
        now = datetime.utcnow()
        if plan_type == 'unlimited':
            user.subscription_end = now + timedelta(days=30)  # 1 month
        elif plan_type == 'low_income':
            user.subscription_end = now + timedelta(days=365)  # 1 year
        elif plan_type == 'pay_per_doc':
            user.subscription_end = None  # No end date for pay-per-document
        
        # Record payment if payment_id is provided
        if payment_id:
            # Determine payment amount based on plan type
            amount = 0
            if plan_type == 'unlimited':
                amount = 50.0
            elif plan_type == 'low_income':
                amount = 25.0
            
            # Create payment record
            payment = Payment(
                user_id=user_id,
                amount=amount,
                payment_type='subscription',
                payment_method='paypal',
                payment_id=payment_id,
                status='completed'
            )
            db.session.add(payment)
        
        # Commit changes
        db.session.commit()
        
        return True, f"Subscription updated to {plan_type}"
    
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")
        return False, f"Error creating subscription: {str(e)}"

def update_document_payment_status(form_id, payment_id):
    """
    Update the payment status for a generated document
    
    Args:
        form_id (int): Form ID
        payment_id (str): Payment ID
        
    Returns:
        tuple: (success, message)
            - success (bool): Whether the operation was successful
            - message (str): Success or error message
    """
    try:
        from app import db
        from models import GeneratedForm, Payment
        
        # Get the form
        form = GeneratedForm.query.get(form_id)
        if not form:
            return False, "Document not found"
        
        # Update form payment status
        form.is_paid = True
        
        # Create payment record
        payment = Payment(
            user_id=form.case.user_id,
            amount=5.99,
            payment_type='per_document',
            payment_method='paypal',
            payment_id=payment_id,
            status='completed',
            generated_form_id=form_id
        )
        db.session.add(payment)
        
        # Commit changes
        db.session.commit()
        
        return True, "Document payment processed successfully"
    
    except Exception as e:
        logger.error(f"Error updating document payment status: {str(e)}")
        return False, f"Error updating payment status: {str(e)}"

def get_subscription_details(user_id):
    """
    Get subscription details for a user
    
    Args:
        user_id (int): User ID
        
    Returns:
        dict: Subscription details
    """
    try:
        from models import User
        
        user = User.query.get(user_id)
        if not user:
            return {
                'status': 'error',
                'message': 'User not found'
            }
        
        # Get subscription details
        subscription_type = user.subscription_type
        subscription_end = user.subscription_end
        
        # Get formatted subscription information
        if subscription_type == 'free':
            status = 'Free Plan'
            expiry = None
        elif subscription_type == 'pay_per_doc':
            status = 'Pay-Per-Document'
            expiry = None
        elif subscription_type == 'unlimited':
            status = 'Unlimited Plan'
            expiry = subscription_end.strftime('%B %d, %Y') if subscription_end else None
        elif subscription_type == 'low_income':
            status = 'Low Income Access'
            expiry = subscription_end.strftime('%B %d, %Y') if subscription_end else None
        else:
            status = 'Unknown'
            expiry = None
        
        # Check if subscription is expired
        is_expired = False
        if subscription_end and subscription_end < datetime.utcnow():
            is_expired = True
        
        return {
            'status': 'success',
            'subscription': {
                'type': subscription_type,
                'name': status,
                'expiry': expiry,
                'is_expired': is_expired
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting subscription details: {str(e)}")
        return {
            'status': 'error',
            'message': f"Error: {str(e)}"
        }
