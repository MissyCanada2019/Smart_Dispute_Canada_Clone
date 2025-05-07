import os
import logging
import re
import json
import random
from datetime import datetime
import requests

# Configure logging
logger = logging.getLogger(__name__)

# Load preset responses for when API is not available
PRESET_RESPONSES = {
    "greeting": [
        "Hello! I'm your AI legal assistant. How can I help you today?",
        "Hi there! I'm here to help with your legal questions. What can I assist you with?",
        "Welcome to SmartDispute.ai! I'm your AI assistant. What legal matter are you dealing with?"
    ],
    "landlord_tenant": [
        "In Ontario, landlords must provide at least 24 hours written notice before entering your unit, except in emergencies. The notice must specify a time between 8am and 8pm.",
        "If your landlord hasn't made necessary repairs, document the issue with photos and written requests. You can file a T6 application with the Landlord and Tenant Board.",
        "Rent increases in Ontario are capped annually by the provincial government. For 2023, the guideline is 2.5%. Your landlord must provide 90 days written notice using the proper form.",
        "If you're facing eviction, you have the right to a hearing at the Landlord and Tenant Board. Don't move out until the Board has made a decision and the Sheriff has enforced it."
    ],
    "credit": [
        "Both Equifax and TransUnion are required to investigate disputes within 30 days. Be sure to provide any supporting documentation with your dispute letter.",
        "Under Canadian law, most negative information stays on your credit report for 6-7 years, depending on the province.",
        "You're entitled to a free copy of your credit report from both Equifax and TransUnion once per year. You can request these online or by mail."
    ],
    "human_rights": [
        "The Human Rights Code in Ontario prohibits discrimination in employment, housing, services, and other areas based on protected grounds like race, gender, disability, and more.",
        "To file a human rights complaint in Ontario, you generally have one year from the incident to submit an application to the Human Rights Tribunal of Ontario.",
        "Employers have a duty to accommodate employees with disabilities up to the point of undue hardship. This may include modifying workspaces, duties, or schedules."
    ],
    "small_claims": [
        "Small Claims Court in Ontario handles civil disputes for claims up to $35,000. The process begins by filing a Plaintiff's Claim (Form 7A).",
        "After filing a claim, you'll need to serve the defendant and file proof of service with the court. The defendant then has 20 days to file a Defence.",
        "Most Small Claims Court cases include a mandatory settlement conference before trial, where a judge tries to help the parties reach an agreement."
    ],
    "document_help": [
        "After generating your document, review it carefully for accuracy. Make sure all personal details and facts about your case are correct.",
        "Once your document is finalized, you'll need to print it, sign where indicated, and make copies. Check the specific filing requirements for your situation.",
        "Our system creates documents based on the information you provide. If your situation is complex, consider having a legal professional review it before filing."
    ],
    "fallback": [
        "I'm still learning about Canadian legal matters. If you have a complex legal situation, it might be best to consult with a legal professional.",
        "I don't have enough information to properly answer that question. Could you provide more details about your situation?",
        "That's a bit outside my area of expertise. I'm focused on helping with landlord-tenant issues, credit disputes, human rights complaints, and other common legal matters in Canada."
    ]
}

def generate_ai_response(message, context=None):
    """
    Generate an AI response to a user message
    
    Args:
        message (str): User message
        context (dict, optional): Additional context information
        
    Returns:
        str: AI response
    """
    try:
        # Try to use OpenAI API if key is set
        openai_api_key = os.environ.get('OPENAI_API_KEY', '')
        
        if openai_api_key:
            return generate_openai_response(message, context, openai_api_key)
        else:
            # Fallback to rule-based responses
            logger.warning("OpenAI API key not set. Using rule-based responses.")
            return generate_rule_based_response(message, context)
    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}")
        return "I'm sorry, I encountered an error processing your request. Please try again."

def generate_openai_response(message, context, api_key):
    """
    Generate a response using the OpenAI API
    
    Args:
        message (str): User message
        context (dict): Additional context information
        api_key (str): OpenAI API key
        
    Returns:
        str: AI response
    """
    try:
        # Build system message with context
        system_message = "You are an AI legal assistant for SmartDispute.ai, a platform that helps Canadians navigate legal systems without a lawyer. "
        system_message += "You provide information about Canadian law, with a focus on Ontario. "
        system_message += "Always mention that you're not giving legal advice, just information. "
        system_message += "Be helpful and professional, but acknowledge when a question is beyond your capabilities. "
        
        # Add case context if available
        if context and 'case' in context:
            case = context['case']
            system_message += f"\nThe user is discussing a case in the category: {case.category}. "
            
            if case.title:
                system_message += f"The case is titled: {case.title}. "
            
            if case.merit_score is not None:
                system_message += f"The case has a merit score of {case.merit_score * 100:.0f}%. "
            
            # Add document context if available
            if 'documents' in context and context['documents']:
                system_message += f"\nThe user has uploaded {len(context['documents'])} documents to this case. "
        
        # Prepare API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": message}
            ],
            "temperature": 0.7,
            "max_tokens": 600
        }
        
        # Make API request
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        # Check for errors
        if response.status_code != 200:
            logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
            return generate_rule_based_response(message, context)
        
        # Extract and return response text
        response_data = response.json()
        ai_response = response_data['choices'][0]['message']['content'].strip()
        
        return ai_response
    
    except Exception as e:
        logger.error(f"Error generating OpenAI response: {str(e)}")
        return generate_rule_based_response(message, context)

def generate_rule_based_response(message, context=None):
    """
    Generate a rule-based response based on the message content
    
    Args:
        message (str): User message
        context (dict, optional): Additional context information
        
    Returns:
        str: AI response
    """
    # Convert message to lowercase for easier matching
    message_lower = message.lower()
    
    # Check for greetings
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
        return random.choice(PRESET_RESPONSES['greeting'])
    
    # Check for different legal domains
    if any(word in message_lower for word in ['landlord', 'tenant', 'rent', 'lease', 'eviction', 'apartment', 'housing']):
        return random.choice(PRESET_RESPONSES['landlord_tenant'])
    
    if any(word in message_lower for word in ['credit', 'equifax', 'transunion', 'report', 'score', 'debt']):
        return random.choice(PRESET_RESPONSES['credit'])
    
    if any(word in message_lower for word in ['discrimination', 'human rights', 'harassment', 'accommodation']):
        return random.choice(PRESET_RESPONSES['human_rights'])
    
    if any(word in message_lower for word in ['small claims', 'sue', 'lawsuit', 'claim', 'court']):
        return random.choice(PRESET_RESPONSES['small_claims'])
    
    if any(word in message_lower for word in ['document', 'form', 'file', 'submit', 'paperwork']):
        return random.choice(PRESET_RESPONSES['document_help'])
    
    # Add context-specific responses if context is available
    if context and 'case' in context:
        case = context['case']
        if case.category == 'landlord-tenant':
            return random.choice(PRESET_RESPONSES['landlord_tenant'])
        elif case.category == 'credit':
            return random.choice(PRESET_RESPONSES['credit'])
        elif case.category == 'human-rights':
            return random.choice(PRESET_RESPONSES['human_rights'])
        elif case.category == 'small-claims':
            return random.choice(PRESET_RESPONSES['small_claims'])
    
    # Fallback response
    return random.choice(PRESET_RESPONSES['fallback'])

def get_document_guidance(form_type):
    """
    Get guidance for filling out a specific document type
    
    Args:
        form_type (str): Type of form
        
    Returns:
        str: Guidance text
    """
    guidance = "Here are some tips for completing this document:\n\n"
    
    if 'landlord-tenant' in form_type:
        if 'maintenance_issues' in form_type:
            guidance += "• Be specific about the maintenance issues (e.g., 'bathroom ceiling leak since January 2023')\n"
            guidance += "• Include dates when you reported the issues to your landlord\n"
            guidance += "• Describe how the issues have affected your use of the rental unit\n"
            guidance += "• For remedies, you can request rent abatement, compensation for damaged belongings, or orders for repairs\n"
        elif 'eviction_defense' in form_type:
            guidance += "• Clearly state why you believe the eviction notice is invalid or issued in bad faith\n"
            guidance += "• Include any evidence that you've paid rent if the eviction is for non-payment\n"
            guidance += "• Mention if the eviction appears to be retaliatory (e.g., after requesting repairs)\n"
    elif 'credit' in form_type:
        guidance += "• Be specific about each item you're disputing (account numbers, dates, amounts)\n"
        guidance += "• Explain why each item is incorrect\n"
        guidance += "• Attach copies (not originals) of supporting documents\n"
        guidance += "• Request that the credit bureau send you an updated report after investigation\n"
    
    guidance += "\nRemember to keep a copy of all documents you submit for your records."
    
    return guidance

def get_next_steps_guidance(form_type):
    """
    Get guidance on next steps after generating a document
    
    Args:
        form_type (str): Type of form
        
    Returns:
        str: Guidance text
    """
    guidance = "After generating this document, here are the next steps:\n\n"
    
    if 'landlord-tenant' in form_type:
        guidance += "1. Review the document for accuracy\n"
        guidance += "2. Sign and date the form\n"
        guidance += "3. Make at least 3 copies (for the LTB, your landlord, and your records)\n"
        guidance += "4. File with the Landlord and Tenant Board (online, by mail, or in person)\n"
        guidance += "5. Pay the filing fee ($53 for most applications)\n"
        guidance += "6. You'll receive a Notice of Hearing with your hearing date\n"
    elif 'credit' in form_type:
        guidance += "1. Print and sign the dispute letter\n"
        guidance += "2. Attach copies of supporting documents\n"
        guidance += "3. Send by certified mail with return receipt requested\n"
        guidance += "4. The credit bureau has 30 days to investigate\n"
        guidance += "5. Follow up if you don't receive a response within 30-45 days\n"
    
    return guidance

def sanitize_user_input(text):
    """
    Sanitize user input to prevent injection attacks
    
    Args:
        text (str): User input text
        
    Returns:
        str: Sanitized text
    """
    # Remove any HTML or JavaScript
    text = re.sub(r'<.*?>', '', text)
    
    # Escape special characters
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#39;')
    
    return text
