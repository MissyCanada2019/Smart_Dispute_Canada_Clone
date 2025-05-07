import os
import logging
import requests
import json
import re

# Configure logging
logger = logging.getLogger(__name__)

# API base URL (placeholder - actual CanLII API might be different)
CANLII_API_BASE_URL = 'https://api.canlii.org/v1'

def get_api_key():
    """Get CanLII API key from environment variables"""
    return os.environ.get('CANLII_API_KEY', '')

def search_canlii(query, jurisdiction='on', document_type='decisions', max_results=10):
    """
    Search CanLII for legal cases or legislation
    
    Args:
        query (str): Search query
        jurisdiction (str): Jurisdiction code (e.g., 'on' for Ontario, 'ca' for Canada)
        document_type (str): Type of document ('decisions' or 'legislation')
        max_results (int): Maximum number of results to return
        
    Returns:
        list: Search results
    """
    api_key = get_api_key()
    if not api_key:
        logger.warning("CanLII API key not set. Using sample data.")
        return get_sample_search_results(query, jurisdiction, document_type)
    
    try:
        # Endpoint URL
        url = f"{CANLII_API_BASE_URL}/search/{document_type}"
        
        # Request parameters
        params = {
            'q': query,
            'jurisdiction': jurisdiction,
            'offset': 0,
            'resultCount': max_results
        }
        
        # Headers
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json'
        }
        
        # Make request
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            return response.json().get('results', [])
        else:
            logger.error(f"Error searching CanLII: {response.status_code} - {response.text}")
            return get_sample_search_results(query, jurisdiction, document_type)
    except Exception as e:
        logger.error(f"Exception searching CanLII: {str(e)}")
        return get_sample_search_results(query, jurisdiction, document_type)

def get_case_details(case_id, database_id):
    """
    Get details of a specific case from CanLII
    
    Args:
        case_id (str): Case identifier
        database_id (str): Database identifier
        
    Returns:
        dict: Case details
    """
    api_key = get_api_key()
    if not api_key:
        logger.warning("CanLII API key not set. Using sample data.")
        return get_sample_case_details(case_id)
    
    try:
        # Endpoint URL
        url = f"{CANLII_API_BASE_URL}/cases/{database_id}/{case_id}"
        
        # Headers
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json'
        }
        
        # Make request
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Error getting case details: {response.status_code} - {response.text}")
            return get_sample_case_details(case_id)
    except Exception as e:
        logger.error(f"Exception getting case details: {str(e)}")
        return get_sample_case_details(case_id)

def get_legislation(legislation_id, jurisdiction='on'):
    """
    Get legislation from CanLII
    
    Args:
        legislation_id (str): Legislation identifier
        jurisdiction (str): Jurisdiction code
        
    Returns:
        dict: Legislation details
    """
    api_key = get_api_key()
    if not api_key:
        logger.warning("CanLII API key not set. Using sample data.")
        return get_sample_legislation(legislation_id, jurisdiction)
    
    try:
        # Endpoint URL
        url = f"{CANLII_API_BASE_URL}/legislation/{jurisdiction}/{legislation_id}"
        
        # Headers
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json'
        }
        
        # Make request
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Error getting legislation: {response.status_code} - {response.text}")
            return get_sample_legislation(legislation_id, jurisdiction)
    except Exception as e:
        logger.error(f"Exception getting legislation: {str(e)}")
        return get_sample_legislation(legislation_id, jurisdiction)

def get_relevant_precedents(category, keywords=None, jurisdiction='on', max_results=5):
    """
    Get relevant precedents for a legal category
    
    Args:
        category (str): Legal category
        keywords (list): Additional keywords for searching
        jurisdiction (str): Jurisdiction code
        max_results (int): Maximum number of results
        
    Returns:
        list: Relevant precedents
    """
    # Map categories to search queries
    category_queries = {
        'landlord-tenant': 'Residential Tenancies Act landlord tenant',
        'credit': 'credit report error dispute',
        'human-rights': 'human rights discrimination',
        'small-claims': 'small claims damages',
        'child-protection': 'child protection welfare',
        'police-misconduct': 'police misconduct complaint'
    }
    
    query = category_queries.get(category, category)
    
    # Add keywords to query if provided
    if keywords and isinstance(keywords, list):
        query = f"{query} {' '.join(keywords)}"
    
    # Search CanLII
    results = search_canlii(query, jurisdiction, 'decisions', max_results)
    
    # Process results
    precedents = []
    for result in results:
        precedent = {
            'title': result.get('title', ''),
            'citation': result.get('citation', ''),
            'snippet': result.get('snippet', ''),
            'url': result.get('url', ''),
            'relevance': result.get('relevance', 0.0)
        }
        precedents.append(precedent)
    
    # Sort by relevance
    precedents = sorted(precedents, key=lambda x: x['relevance'], reverse=True)
    
    return precedents

def get_sample_search_results(query, jurisdiction, document_type):
    """
    Get sample search results for testing without API
    
    Args:
        query (str): Search query
        jurisdiction (str): Jurisdiction code
        document_type (str): Document type
        
    Returns:
        list: Sample search results
    """
    # Sample results for testing
    sample_results = [
        {
            'title': 'Smith v. Jones, 2021 ONSC 123',
            'citation': '2021 ONSC 123',
            'snippet': 'The court found that the landlord\'s failure to address the persistent mold issue constituted a material breach of the tenancy agreement...',
            'url': 'https://www.canlii.org/en/on/onsc/doc/2021/2021onsc123/2021onsc123.html',
            'relevance': 0.85
        },
        {
            'title': 'R. v. Brown, 2019 ONCA 456',
            'citation': '2019 ONCA 456',
            'snippet': 'The appellant argued that the police search was unreasonable and violated his Charter rights under section 8...',
            'url': 'https://www.canlii.org/en/on/onca/doc/2019/2019onca456/2019onca456.html',
            'relevance': 0.72
        },
        {
            'title': 'Residential Tenancies Act, 2006, S.O. 2006, c. 17',
            'citation': 'S.O. 2006, c. 17',
            'snippet': 'Section 22 specifies that a landlord is responsible for maintaining the rental unit in a good state of repair and fit for habitation...',
            'url': 'https://www.canlii.org/en/on/laws/stat/so-2006-c-17/latest/so-2006-c-17.html',
            'relevance': 0.91
        }
    ]
    
    # Filter results by document type
    if document_type == 'decisions':
        results = [r for r in sample_results if 'v.' in r['title']]
    else:  # legislation
        results = [r for r in sample_results if 'Act' in r['title'] or 'Code' in r['title']]
    
    return results

def get_sample_case_details(case_id):
    """
    Get sample case details for testing without API
    
    Args:
        case_id (str): Case identifier
        
    Returns:
        dict: Sample case details
    """
    # Sample case details
    return {
        'title': 'Smith v. Jones',
        'citation': '2021 ONSC 123',
        'docket': 'CV-21-00123456-0000',
        'date': '2021-05-15',
        'court': 'Ontario Superior Court of Justice',
        'judges': ['Justice A. Smith'],
        'full_text': 'This is a sample case full text. It would normally contain the complete text of the decision...',
        'keywords': ['landlord', 'tenant', 'repair', 'mold', 'breach of contract']
    }

def get_sample_legislation(legislation_id, jurisdiction):
    """
    Get sample legislation for testing without API
    
    Args:
        legislation_id (str): Legislation identifier
        jurisdiction (str): Jurisdiction code
        
    Returns:
        dict: Sample legislation details
    """
    # Sample legislation details
    sample_legislations = {
        'residential-tenancies-act': {
            'title': 'Residential Tenancies Act, 2006',
            'citation': 'S.O. 2006, c. 17',
            'jurisdiction': 'Ontario',
            'sections': [
                {
                    'number': '20',
                    'title': 'Landlord\'s responsibility to repair',
                    'text': 'A landlord is responsible for providing and maintaining a residential complex, including the rental units in it, in a good state of repair and fit for habitation and for complying with health, safety, housing and maintenance standards.'
                },
                {
                    'number': '22',
                    'title': 'Landlord\'s responsibility re services',
                    'text': 'A landlord shall not at any time during a tenant\'s occupancy of a rental unit and before the day on which an order evicting the tenant is executed, withhold the reasonable supply of any vital service, care service or food that it is the landlord\'s obligation to supply under the tenancy agreement or deliberately interfere with the reasonable supply of any vital service, care service or food.'
                }
            ]
        },
        'human-rights-code': {
            'title': 'Human Rights Code',
            'citation': 'R.S.O. 1990, c. H.19',
            'jurisdiction': 'Ontario',
            'sections': [
                {
                    'number': '2',
                    'title': 'Accommodation',
                    'text': 'Every person has a right to equal treatment with respect to the occupancy of accommodation, without discrimination because of race, ancestry, place of origin, colour, ethnic origin, citizenship, creed, sex, sexual orientation, gender identity, gender expression, age, marital status, family status, disability or the receipt of public assistance.'
                }
            ]
        }
    }
    
    # Get legislation by ID or return a default one
    return sample_legislations.get(legislation_id, {
        'title': 'Sample Legislation',
        'citation': 'Sample Citation',
        'jurisdiction': jurisdiction.upper(),
        'sections': [
            {
                'number': '1',
                'title': 'Sample Section',
                'text': 'This is a sample section text...'
            }
        ]
    })
