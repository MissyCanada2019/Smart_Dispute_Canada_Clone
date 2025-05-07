import os
import uuid
import logging
from datetime import datetime, timedelta
import random

# Configure logging
logger = logging.getLogger(__name__)

def calculate_mailing_cost(mailing):
    """
    Calculate the cost for a mailing request
    
    Args:
        mailing: MailingRequest object or dictionary with mailing details
        
    Returns:
        float: Total cost for the mailing request
    """
    # Get mail type and other details
    if hasattr(mailing, 'mail_type'):
        # MailingRequest object
        mail_type = mailing.mail_type
        include_copies = mailing.include_copies
        copy_count = mailing.copy_count
        page_count = mailing.page_count
        destination_type = mailing.destination_type
    else:
        # Dictionary with mailing details
        mail_type = mailing.get('mail_type')
        include_copies = mailing.get('include_copies', False)
        copy_count = mailing.get('copy_count', 0)
        page_count = mailing.get('page_count', 1)
        destination_type = mailing.get('destination_type')
    
    # Base cost by mail type
    base_cost = calculate_base_mailing_cost(mailing)
    
    # Additional cost for copies
    copy_cost = calculate_copy_cost(mailing)
    
    # Calculate total cost
    total_cost = base_cost + copy_cost
    
    # Round to 2 decimal places
    total_cost = round(total_cost, 2)
    
    return total_cost

def calculate_base_mailing_cost(mailing):
    """Calculate the base cost for mailing based on mail type and destination"""
    # Get mail type and other details
    if hasattr(mailing, 'mail_type'):
        # MailingRequest object
        mail_type = mailing.mail_type
        destination_type = mailing.destination_type
    else:
        # Dictionary with mailing details
        mail_type = mailing.get('mail_type')
        destination_type = mailing.get('destination_type')
    
    # Base costs by mail type
    if mail_type == 'regular':
        base_cost = 2.50
    elif mail_type == 'express':
        base_cost = 12.00
    elif mail_type == 'certified':
        base_cost = 18.00
    else:
        base_cost = 2.50  # Default to regular mail cost
    
    # Adjust based on destination type
    if destination_type == 'court':
        # Courts often require certified mail
        if mail_type == 'regular':
            base_cost += 2.00  # Surcharge for court filings
    elif destination_type == 'agency':
        # Government agencies may have special handling
        base_cost += 1.00
    
    return base_cost

def calculate_copy_cost(mailing):
    """Calculate the cost for additional copies"""
    # Get copy details
    if hasattr(mailing, 'include_copies'):
        # MailingRequest object
        include_copies = mailing.include_copies
        copy_count = mailing.copy_count
        page_count = mailing.page_count
    else:
        # Dictionary with mailing details
        include_copies = mailing.get('include_copies', False)
        copy_count = mailing.get('copy_count', 0)
        page_count = mailing.get('page_count', 1)
    
    # Calculate copy cost
    if include_copies and copy_count > 0:
        cost_per_page = 0.15  # Cost per page for copies
        return copy_count * page_count * cost_per_page
    
    return 0.0

def create_mailing_request(user_id, form_id, document_path, mailing_details):
    """
    Create a mailing request for a document
    
    Args:
        user_id: User ID
        form_id: Generated form ID
        document_path: Path to the document file
        mailing_details: Dictionary with mailing details
        
    Returns:
        dict: Result with success flag and mailing request details
    """
    try:
        # Validate mailing address
        recipient_address = mailing_details.get('recipient_address')
        if not recipient_address:
            return {'success': False, 'error': 'Recipient address is required'}
        
        # Validate recipient address
        address_validation = validate_mailing_address(recipient_address)
        if not address_validation['is_valid']:
            return {'success': False, 'error': f"Invalid recipient address: {address_validation['error']}"}
        
        # Validate return address if provided
        return_address = mailing_details.get('return_address')
        if return_address:
            return_validation = validate_mailing_address(return_address)
            if not return_validation['is_valid']:
                return {'success': False, 'error': f"Invalid return address: {return_validation['error']}"}
        
        # Generate unique reference number
        reference_number = generate_reference_number()
        
        # Calculate costs
        mail_type = mailing_details.get('mail_type')
        include_copies = mailing_details.get('include_copies', False)
        copy_count = mailing_details.get('copy_count', 0) if include_copies else 0
        page_count = mailing_details.get('page_count', 1)
        destination_type = mailing_details.get('destination_type')
        
        # Create cost details
        cost_details = {
            'base_cost': calculate_base_mailing_cost({
                'mail_type': mail_type,
                'destination_type': destination_type
            }),
            'copy_cost': calculate_copy_cost({
                'include_copies': include_copies,
                'copy_count': copy_count,
                'page_count': page_count
            }),
            'total_cost': calculate_mailing_cost({
                'mail_type': mail_type,
                'include_copies': include_copies,
                'copy_count': copy_count,
                'page_count': page_count,
                'destination_type': destination_type
            })
        }
        
        # Create mailing request details
        mailing_request = {
            'reference_number': reference_number,
            'user_id': user_id,
            'form_id': form_id,
            'document_path': document_path,
            'mail_type': mail_type,
            'recipient_address': recipient_address,
            'return_address': return_address,
            'include_copies': include_copies,
            'copy_count': copy_count,
            'page_count': page_count,
            'destination_type': destination_type,
            'status': 'pending',
            'cost_details': cost_details,
            'created_at': datetime.utcnow().isoformat()
        }
        
        # In a real implementation, this would save the request to a mailing service
        # and return a tracking number or reference number
        logger.info(f"Created mailing request with reference {reference_number}")
        
        return {'success': True, 'mailing_request': mailing_request}
    except Exception as e:
        logger.error(f"Error creating mailing request: {str(e)}")
        return {'success': False, 'error': str(e)}

def validate_mailing_address(address):
    """
    Validate a mailing address
    
    Args:
        address: Dictionary with address details
        
    Returns:
        dict: Validation result with is_valid flag and error message if invalid
    """
    # Check for required fields
    required_fields = ['recipient_name', 'street_address', 'city', 'province', 'postal_code']
    missing_fields = [field for field in required_fields if not address.get(field)]
    
    if missing_fields:
        return {
            'is_valid': False,
            'error': f"Missing required fields: {', '.join(missing_fields)}"
        }
    
    # Check postal code format (Canadian postal code)
    postal_code = address.get('postal_code', '').strip().upper()
    if not is_valid_canadian_postal_code(postal_code):
        return {
            'is_valid': False,
            'error': "Invalid Canadian postal code format"
        }
    
    # Check province (must be a valid Canadian province/territory)
    province = address.get('province', '').strip().upper()
    if not is_valid_canadian_province(province):
        return {
            'is_valid': False,
            'error': "Invalid Canadian province/territory"
        }
    
    return {'is_valid': True}

def is_valid_canadian_postal_code(postal_code):
    """
    Check if a postal code is in valid Canadian format (A1A 1A1)
    """
    if not postal_code:
        return False
    
    # Remove spaces and standardize format
    postal_code = postal_code.strip().upper().replace(' ', '')
    
    # Check length
    if len(postal_code) != 6:
        return False
    
    # Check format (letter-number-letter-number-letter-number)
    return (postal_code[0].isalpha() and
            postal_code[1].isdigit() and
            postal_code[2].isalpha() and
            postal_code[3].isdigit() and
            postal_code[4].isalpha() and
            postal_code[5].isdigit())

def is_valid_canadian_province(province):
    """
    Check if a province/territory is valid for Canada
    """
    valid_provinces = [
        'AB', 'BC', 'MB', 'NB', 'NL', 'NS', 'NT', 'NU', 'ON', 'PE', 'QC', 'SK', 'YT',
        'ALBERTA', 'BRITISH COLUMBIA', 'MANITOBA', 'NEW BRUNSWICK', 'NEWFOUNDLAND AND LABRADOR',
        'NOVA SCOTIA', 'NORTHWEST TERRITORIES', 'NUNAVUT', 'ONTARIO', 'PRINCE EDWARD ISLAND',
        'QUEBEC', 'SASKATCHEWAN', 'YUKON'
    ]
    
    return province.strip().upper() in valid_provinces

def generate_reference_number():
    """
    Generate a unique reference number for mailing requests
    """
    # Format: SD-YYYYMMDD-XXXXX (SD for SmartDispute, date, and 5 random characters)
    date_part = datetime.utcnow().strftime('%Y%m%d')
    random_part = ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ23456789', k=5))  # Exclude confusing chars
    
    return f"SD-{date_part}-{random_part}"

def get_mailing_request_status(reference_number):
    """
    Get the current status of a mailing request
    
    Args:
        reference_number: Mailing request reference number
        
    Returns:
        dict: Status details or None if not found
    """
    # In a real implementation, this would query a mailing service API
    # For now, generate a random status based on the reference number
    
    # Extract the date part from the reference number
    date_parts = reference_number.split('-')
    if len(date_parts) != 3:
        return None
    
    date_str = date_parts[1]
    try:
        request_date = datetime.strptime(date_str, '%Y%m%d')
        days_since_request = (datetime.utcnow() - request_date).days
        
        # Simulate status based on days since request
        if days_since_request < 1:
            status = 'processing'
            tracking_number = None
            estimated_delivery = None
        elif days_since_request < 2:
            status = 'shipped'
            tracking_number = f"TRK{date_str}{random.randint(1000, 9999)}"
            estimated_delivery = (request_date + timedelta(days=5)).isoformat()
        elif days_since_request < 7:
            status = 'in_transit'
            tracking_number = f"TRK{date_str}{random.randint(1000, 9999)}"
            estimated_delivery = (request_date + timedelta(days=5)).isoformat()
        else:
            status = 'delivered'
            tracking_number = f"TRK{date_str}{random.randint(1000, 9999)}"
            estimated_delivery = (request_date + timedelta(days=5)).isoformat()
        
        return {
            'reference_number': reference_number,
            'status': status,
            'tracking_number': tracking_number,
            'estimated_delivery': estimated_delivery
        }
    except ValueError:
        return None

def get_available_mailing_options():
    """
    Get available mailing options and pricing
    
    Returns:
        dict: Available mailing options and pricing
    """
    return {
        'regular': {
            'name': 'Regular Mail',
            'description': 'Standard postal mail (5-7 business days)',
            'base_price': 2.50
        },
        'express': {
            'name': 'Express Mail',
            'description': 'Expedited postal service (2-3 business days)',
            'base_price': 12.00
        },
        'certified': {
            'name': 'Certified Mail',
            'description': 'Includes proof of mailing and delivery confirmation (3-5 business days)',
            'base_price': 18.00
        }
    }

def queue_mailing_request(mailing_request):
    """
    Queue a mailing request for processing
    
    Args:
        mailing_request: MailingRequest object
        
    Returns:
        bool: Success flag
    """
    try:
        # In a real implementation, this would send the request to a mailing service
        # or add it to a processing queue
        
        # Log the queuing of the request
        if hasattr(mailing_request, 'id'):
            logger.info(f"Queued mailing request ID {mailing_request.id} with reference {mailing_request.reference_number}")
        else:
            logger.info(f"Queued mailing request with reference {mailing_request.get('reference_number')}")
        
        # Simulate successful queuing
        return True
    except Exception as e:
        logger.error(f"Error queuing mailing request: {str(e)}")
        return False