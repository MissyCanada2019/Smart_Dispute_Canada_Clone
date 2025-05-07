import logging
import re
import json
import os
from collections import Counter

# Configure logging
logger = logging.getLogger(__name__)

# Sample classification data - in a real implementation, this would be more sophisticated
# and likely backed by a machine learning model or more extensive rules
LEGAL_CATEGORIES = {
    'landlord-tenant': {
        'keywords': [
            'landlord', 'tenant', 'rent', 'lease', 'eviction', 'N4', 'L1', 'T2', 'T6', 
            'maintenance', 'repair', 'mold', 'infestation', 'deposit', 'unit', 'apartment',
            'rental', 'property manager', 'housing', 'LTB', 'Landlord and Tenant Board'
        ],
        'forms': {
            'eviction_defense': {
                'name': 'Eviction Defense (LTB Form T5)',
                'description': 'Use when contesting an eviction notice',
                'required_keywords': ['eviction', 'N4', 'N5', 'notice', 'terminate']
            },
            'maintenance_issues': {
                'name': 'Maintenance Issues Complaint (LTB Form T6)',
                'description': 'Use when your landlord has failed to maintain your unit',
                'required_keywords': ['repair', 'maintenance', 'mold', 'broken', 'fix', 'condition']
            },
            'illegal_rent_increase': {
                'name': 'Illegal Rent Increase Dispute (LTB Form T1)',
                'description': 'Use when your landlord has illegally increased your rent',
                'required_keywords': ['rent', 'increase', 'notice', 'illegal', 'amount']
            },
            'harassment': {
                'name': 'Landlord Harassment Complaint (LTB Form T2)',
                'description': 'Use when your landlord is harassing or interfering with your tenancy',
                'required_keywords': ['harassment', 'interfere', 'threat', 'privacy', 'entry']
            }
        }
    },
    'credit': {
        'keywords': [
            'credit', 'report', 'score', 'bureau', 'equifax', 'transunion', 'debt', 
            'collection', 'error', 'dispute', 'account', 'payment', 'late', 'default',
            'bankruptcy', 'consumer', 'reporting agency'
        ],
        'forms': {
            'report_dispute': {
                'name': 'Credit Report Dispute Letter',
                'description': 'Use to dispute errors on your credit report',
                'required_keywords': ['error', 'dispute', 'report', 'inaccurate', 'incorrect']
            },
            'collection_validation': {
                'name': 'Debt Collection Validation Request',
                'description': 'Use to request validation of a debt from collectors',
                'required_keywords': ['debt', 'collection', 'collector', 'validate', 'proof']
            }
        }
    },
    'human-rights': {
        'keywords': [
            'discrimination', 'human rights', 'accommodation', 'disability', 
            'harassment', 'protected ground', 'gender', 'race', 'religion', 'sexual orientation',
            'equal', 'tribunal', 'HRTO', 'human rights tribunal', 'complaint'
        ],
        'forms': {
            'hrto_complaint': {
                'name': 'Human Rights Tribunal of Ontario Complaint',
                'description': 'Use to file a complaint about discrimination with the HRTO',
                'required_keywords': ['discrimination', 'human rights', 'protected ground']
            },
            'accommodation_request': {
                'name': 'Accommodation Request Letter',
                'description': 'Use to request accommodation for a disability or protected ground',
                'required_keywords': ['accommodation', 'disability', 'require', 'need']
            }
        }
    },
    'small-claims': {
        'keywords': [
            'claim', 'court', 'small claims', 'plaintiff', 'defendant', 'sue', 
            'damages', 'breach', 'contract', 'payment', 'debt', 'owed', 'agreement',
            'service', 'goods', 'money', 'compensation'
        ],
        'forms': {
            'statement_of_claim': {
                'name': 'Statement of Claim (Form 7A)',
                'description': 'Use to start a lawsuit in Small Claims Court',
                'required_keywords': ['claim', 'sue', 'owed', 'damages', 'breach']
            },
            'defense': {
                'name': 'Defense (Form 9A)',
                'description': 'Use to defend against a claim made against you',
                'required_keywords': ['defend', 'defendant', 'against', 'claim']
            }
        }
    },
    'child-protection': {
        'keywords': [
            'child', 'children', 'CAS', 'Children\'s Aid Society', 'protection', 
            'welfare', 'custody', 'access', 'care', 'guardian', 'parent', 'supervision',
            'apprehension', 'abuse', 'neglect', 'safety'
        ],
        'forms': {
            'cas_response': {
                'name': 'Response to Child Protection Application',
                'description': 'Use to respond to a CAS court application about your child',
                'required_keywords': ['CAS', 'application', 'child', 'protection', 'court']
            },
            'access_request': {
                'name': 'Access Request Form',
                'description': 'Use to request access to your child in CAS care',
                'required_keywords': ['access', 'child', 'visit', 'care', 'parent']
            }
        }
    },
    'police-misconduct': {
        'keywords': [
            'police', 'officer', 'misconduct', 'complaint', 'brutality', 
            'excessive force', 'arrest', 'detained', 'rights', 'OIPRD', 
            'investigation', 'badge', 'number', 'incident'
        ],
        'forms': {
            'oiprd_complaint': {
                'name': 'OIPRD Police Complaint Form',
                'description': 'Use to file a complaint about police misconduct',
                'required_keywords': ['police', 'misconduct', 'complaint', 'officer']
            },
            'disclosure_request': {
                'name': 'Police Records Disclosure Request',
                'description': 'Use to request disclosure of police records about an incident',
                'required_keywords': ['police', 'record', 'disclosure', 'incident', 'report']
            }
        }
    }
}

def analyze_case(case, documents):
    """
    Analyze case based on documents to identify legal issues and relevant information
    
    Args:
        case: Case model instance
        documents: List of Document model instances
        
    Returns:
        dict: Analysis results
    """
    try:
        # Combine text from all documents
        combined_text = " ".join([doc.extracted_text or "" for doc in documents])
        
        # Extract dates and names from document metadata
        all_dates = []
        all_names = []
        for doc in documents:
            metadata = doc.metadata or {}
            all_dates.extend(metadata.get('dates', []))
            all_names.extend(metadata.get('names', []))
        
        # Identify legal categories and issues
        category_scores = {}
        for category, data in LEGAL_CATEGORIES.items():
            keywords = data['keywords']
            score = 0
            for keyword in keywords:
                # Search for keyword in case-insensitive manner
                matches = re.findall(r'\b' + re.escape(keyword) + r'\b', combined_text, re.IGNORECASE)
                score += len(matches)
            
            category_scores[category] = score
        
        # Find highest scoring categories
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Identify detected issues based on keywords
        detected_issues = []
        for category, score in sorted_categories[:2]:  # Consider top 2 categories
            if score > 0:
                category_data = LEGAL_CATEGORIES[category]
                for form_key, form_data in category_data['forms'].items():
                    issue_score = 0
                    for keyword in form_data['required_keywords']:
                        matches = re.findall(r'\b' + re.escape(keyword) + r'\b', combined_text, re.IGNORECASE)
                        issue_score += len(matches)
                    
                    if issue_score > 0:
                        detected_issues.append({
                            'category': category,
                            'issue_type': form_key,
                            'name': form_data['name'],
                            'description': form_data['description'],
                            'score': issue_score
                        })
        
        # Extract key entities (like addresses, phone numbers, etc.)
        key_entities = {}
        for doc in documents:
            metadata = doc.metadata or {}
            for entity_type in ['addresses', 'phone_numbers', 'email_addresses']:
                if entity_type not in key_entities:
                    key_entities[entity_type] = []
                key_entities[entity_type].extend(metadata.get(entity_type, []))
        
        # Remove duplicates
        for entity_type in key_entities:
            key_entities[entity_type] = list(set(key_entities[entity_type]))
        
        # Create analysis result
        analysis = {
            'case_id': case.id,
            'category_scores': category_scores,
            'detected_issues': sorted(detected_issues, key=lambda x: x['score'], reverse=True),
            'key_entities': key_entities,
            'dates': list(set(all_dates)),
            'names': list(set(all_names))
        }
        
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing case: {str(e)}")
        return {
            'case_id': case.id,
            'category_scores': {},
            'detected_issues': [],
            'key_entities': {},
            'dates': [],
            'names': []
        }

def get_merit_score(analysis):
    """
    Calculate a merit score for the case based on analysis
    
    Args:
        analysis: Dict containing case analysis
        
    Returns:
        float: Merit score between 0.0 and 1.0
    """
    try:
        # Base factors for merit calculation
        evidence_strength = 0.0
        issue_clarity = 0.0
        entity_completeness = 0.0
        
        # Evidence strength based on number of documents and entities found
        entity_count = sum(len(entities) for entity_type, entities in analysis.get('key_entities', {}).items())
        evidence_strength = min(0.5, entity_count / 10)
        
        # Issue clarity based on detected issues
        detected_issues = analysis.get('detected_issues', [])
        if detected_issues:
            top_issue_score = detected_issues[0].get('score', 0)
            issue_clarity = min(0.5, top_issue_score / 10)
        
        # Entity completeness checks if we have addresses, names, and dates
        has_addresses = len(analysis.get('key_entities', {}).get('addresses', [])) > 0
        has_names = len(analysis.get('names', [])) > 0
        has_dates = len(analysis.get('dates', [])) > 0
        
        entity_completeness = (has_addresses + has_names + has_dates) / 6
        
        # Calculate final merit score
        merit_score = evidence_strength + issue_clarity + entity_completeness
        
        # Normalize to 0.0-1.0 range
        normalized_score = min(1.0, merit_score)
        
        return round(normalized_score, 2)
    except Exception as e:
        logger.error(f"Error calculating merit score: {str(e)}")
        return 0.0

def get_recommended_forms(category, analysis):
    """
    Get recommended legal forms based on category and analysis
    
    Args:
        category: Legal category (e.g., 'landlord-tenant')
        analysis: Dict containing case analysis
        
    Returns:
        list: Recommended forms
    """
    try:
        recommended_forms = []
        
        # Get top detected issues
        detected_issues = analysis.get('detected_issues', [])
        
        # If we have detected issues, use those forms
        if detected_issues:
            for issue in detected_issues:
                form_category = issue.get('category')
                issue_type = issue.get('issue_type')
                
                if form_category and issue_type and form_category in LEGAL_CATEGORIES:
                    form_data = LEGAL_CATEGORIES[form_category]['forms'].get(issue_type)
                    if form_data:
                        recommended_forms.append({
                            'id': f"{form_category}_{issue_type}",
                            'name': form_data['name'],
                            'description': form_data['description'],
                            'category': form_category,
                            'score': issue.get('score', 0)
                        })
        
        # If no issues detected or if the category doesn't match detected issues,
        # recommend general forms for the specified category
        if not recommended_forms or all(form['category'] != category for form in recommended_forms):
            if category in LEGAL_CATEGORIES:
                for issue_type, form_data in LEGAL_CATEGORIES[category]['forms'].items():
                    recommended_forms.append({
                        'id': f"{category}_{issue_type}",
                        'name': form_data['name'],
                        'description': form_data['description'],
                        'category': category,
                        'score': 0  # Default score
                    })
        
        # Sort by score (highest first)
        recommended_forms = sorted(recommended_forms, key=lambda x: x['score'], reverse=True)
        
        return recommended_forms
    except Exception as e:
        logger.error(f"Error getting recommended forms: {str(e)}")
        return []

def get_relevant_precedents(category, analysis):
    """
    Get relevant legal precedents based on category and analysis
    This is a placeholder that would normally call the CanLII API
    
    Args:
        category: Legal category
        analysis: Dict containing case analysis
        
    Returns:
        list: Relevant precedents
    """
    # This would normally call the CanLII API or database
    # For now, return hardcoded sample precedents for each category
    try:
        sample_precedents = {
            'landlord-tenant': [
                {
                    'title': 'Oakwood v Jen, 2023 CanLII 15323 (ON LTB)',
                    'citation': '2023 CanLII 15323 (ON LTB)',
                    'snippet': 'The Board finds that the persistent water leakage constitutes a serious breach of the landlord\'s maintenance obligations under s. 20 of the RTA...',
                    'relevance': 0.85,
                    'url': 'https://www.canlii.org/en/on/onltb/doc/2023/2023canlii15323/'
                },
                {
                    'title': 'Metropolitan Toronto Housing Authority v. Godwin, 2002 CanLII 20651 (ON LTB)',
                    'citation': '2002 CanLII 20651 (ON LTB)',
                    'snippet': 'The tenant has a right to organize and the landlord cannot interfere with this right through harassment or threatening eviction...',
                    'relevance': 0.72,
                    'url': 'https://www.canlii.org/en/on/onltb/doc/2002/2002canlii20651/'
                }
            ],
            'credit': [
                {
                    'title': 'Haskett v. Equifax Canada Inc., 2003 CanLII 32896 (ON CA)',
                    'citation': '2003 CanLII 32896 (ON CA)',
                    'snippet': 'Credit reporting agencies have a duty to maintain accurate information and to correct errors promptly when notified...',
                    'relevance': 0.79,
                    'url': 'https://www.canlii.org/en/on/onca/doc/2003/2003canlii32896/'
                }
            ],
            'human-rights': [
                {
                    'title': 'Johnstone v. Canada (Border Services Agency), 2014 FCA 110',
                    'citation': '2014 FCA 110',
                    'snippet': 'Employers have a duty to accommodate employees with family status obligations, including childcare responsibilities...',
                    'relevance': 0.81,
                    'url': 'https://www.canlii.org/en/ca/fca/doc/2014/2014fca110/'
                }
            ],
            'small-claims': [
                {
                    'title': 'Garland v. Consumers\' Gas Co., 2004 SCC 25',
                    'citation': '2004 SCC 25',
                    'snippet': 'The court established the test for unjust enrichment as: (1) enrichment of the defendant; (2) corresponding deprivation of the plaintiff; and (3) absence of juristic reason...',
                    'relevance': 0.68,
                    'url': 'https://www.canlii.org/en/ca/scc/doc/2004/2004scc25/'
                }
            ],
            'child-protection': [
                {
                    'title': 'Children\'s Aid Society of Toronto v. L.P., 2010 ONCJ 320',
                    'citation': '2010 ONCJ 320',
                    'snippet': 'The court must consider the least restrictive alternative that can adequately protect the child when making an order...',
                    'relevance': 0.77,
                    'url': 'https://www.canlii.org/en/on/oncj/doc/2010/2010oncj320/'
                }
            ],
            'police-misconduct': [
                {
                    'title': 'Schaeffer v. Wood, 2013 SCC 71',
                    'citation': '2013 SCC 71',
                    'snippet': 'Police officers involved in investigations of incidents where there has been serious injury or death do not have the right to consult with counsel before preparing their notes...',
                    'relevance': 0.75,
                    'url': 'https://www.canlii.org/en/ca/scc/doc/2013/2013scc71/'
                }
            ]
        }
        
        # Get precedents for the specified category
        precedents = sample_precedents.get(category, [])
        
        # If there are detected issues, try to find more specific precedents
        detected_issues = analysis.get('detected_issues', [])
        if detected_issues:
            # This would normally search for more specific precedents based on issues
            # For now, just return the general category precedents
            pass
        
        return precedents
    except Exception as e:
        logger.error(f"Error getting relevant precedents: {str(e)}")
        return []
