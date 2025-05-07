import logging
import re
import json
import os
from collections import Counter
from datetime import datetime

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
        # Initialize OpenAI API client if available for advanced analysis
        use_ai_enhanced_analysis = False
        try:
            # Check if we have an OpenAI API key
            api_key = os.environ.get('OPENAI_API_KEY')
            if api_key and api_key.strip():
                try:
                    from openai import OpenAI
                    client = OpenAI(api_key=api_key)
                    use_ai_enhanced_analysis = True
                    logger.info("Using AI-enhanced document analysis")
                except ImportError:
                    logger.warning("OpenAI package not available, falling back to rule-based analysis")
            else:
                logger.warning("OpenAI API key not set or empty, falling back to rule-based analysis")
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {str(e)}")
            # Continue with rule-based analysis
        
        # Combine text from all documents
        all_texts = [doc.extracted_text or "" for doc in documents]
        combined_text = " ".join(all_texts)
        
        # Extract dates and names from document metadata
        all_dates = []
        all_names = []
        for doc in documents:
            metadata = doc.doc_metadata or {}
            all_dates.extend(metadata.get('dates', []))
            all_names.extend(metadata.get('names', []))
        
        # Weight the document texts by recency and type
        weighted_docs = []
        for doc in documents:
            doc_type = doc.file_type.lower() if doc.file_type else ""
            # Give higher weight to recent documents and official forms
            weight = 1.0
            if "official" in doc.filename.lower() or "form" in doc.filename.lower():
                weight = 2.0
            if "court" in doc.filename.lower() or "notice" in doc.filename.lower():
                weight = 2.5
            
            weighted_docs.append({
                "text": doc.extracted_text or "",
                "weight": weight,
                "type": doc_type
            })
        
        # AI-enhanced analysis if available
        ai_insights = {}
        if use_ai_enhanced_analysis and combined_text.strip():
            try:
                # Prepare a concise version of the text for API limits
                condensed_text = combined_text[:10000]  # Limit to first 10,000 chars for API limits
                
                # Query OpenAI for enhanced analysis
                response = client.chat.completions.create(
                    model="gpt-4o",  # Use the newest available model (released May 13, 2024)
                    messages=[
                        {"role": "system", "content": "You are a legal analysis assistant specializing in Canadian law. Analyze the provided document text and extract key legal issues, relevant laws, and case assessment."},
                        {"role": "user", "content": f"Case category: {case.category}. Analyze the following document text to identify specific legal issues, applicable Canadian laws, and assess case strength: {condensed_text}"}
                    ],
                    response_format={"type": "json_object"}
                )
                
                ai_analysis = json.loads(response.choices[0].message.content)
                
                # Extract insights from AI analysis
                if isinstance(ai_analysis, dict):
                    ai_insights = {
                        "legal_issues": ai_analysis.get("legal_issues", []),
                        "applicable_laws": ai_analysis.get("applicable_laws", []),
                        "case_assessment": ai_analysis.get("case_assessment", {}),
                        "suggested_actions": ai_analysis.get("suggested_actions", [])
                    }
                    logger.info("AI analysis successful")
            except Exception as ai_error:
                logger.error(f"AI analysis error: {str(ai_error)}")
                # Continue with rule-based analysis
        
        # Rule-based category and issue detection (enhanced)
        category_scores = {}
        # First pass: identify document frequency of keywords
        keyword_freq = Counter()
        for category, data in LEGAL_CATEGORIES.items():
            keywords = data['keywords']
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                # Count documents containing this keyword
                doc_count = sum(1 for doc in all_texts if re.search(pattern, doc, re.IGNORECASE))
                if doc_count > 0:
                    keyword_freq[keyword] = doc_count
        
        # Second pass: score categories with TF-IDF-like approach
        total_docs = len(all_texts) or 1  # Avoid division by zero
        for category, data in LEGAL_CATEGORIES.items():
            keywords = data['keywords']
            score = 0
            
            # Calculate category score based on keyword frequency and document distribution
            for keyword in keywords:
                # Search for keyword in case-insensitive manner across all text
                matches = re.findall(r'\b' + re.escape(keyword) + r'\b', combined_text, re.IGNORECASE)
                keyword_count = len(matches)
                
                # Document frequency component (how many docs contain this keyword)
                doc_freq = keyword_freq.get(keyword, 0) / total_docs
                
                # Term frequency component (how often keyword appears overall)
                term_freq = keyword_count / (len(combined_text.split()) or 1)  # Avoid division by zero
                
                # Combined TF-IDF-like score
                keyword_score = keyword_count * (1 + doc_freq) * 100
                
                # Give higher weight to specialized terms vs common terms
                if len(keyword.split()) > 1:  # Multi-word terms are more specific
                    keyword_score *= 1.5
                
                score += keyword_score
            
            category_scores[category] = round(score, 2)
        
        # Find highest scoring categories
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Context-aware issue detection
        detected_issues = []
        context_windows = []
        
        # Create context windows around key terms to better understand their usage
        for category, score in sorted_categories[:3]:  # Consider top 3 categories
            if score > 0:
                category_data = LEGAL_CATEGORIES[category]
                for form_key, form_data in category_data['forms'].items():
                    issue_score = 0
                    issue_context = []
                    
                    for keyword in form_data['required_keywords']:
                        pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
                        
                        # Check each document for contextual matches
                        for doc_text in all_texts:
                            for match in pattern.finditer(doc_text):
                                # Get context window (50 chars before and after the match)
                                start = max(0, match.start() - 50)
                                end = min(len(doc_text), match.end() + 50)
                                context = doc_text[start:end]
                                issue_context.append(context)
                                issue_score += 1
                    
                    # Calculate confidence based on keyword matches and context
                    keyword_match_count = len(issue_context)
                    
                    # Add additional confidence if multiple keywords are found close together
                    contextual_bonus = 0
                    if len(issue_context) >= 2:
                        contextual_bonus = len(issue_context) * 0.5
                    
                    total_issue_score = issue_score + contextual_bonus
                    
                    if total_issue_score > 0:
                        detected_issues.append({
                            'category': category,
                            'issue_type': form_key,
                            'name': form_data['name'],
                            'description': form_data['description'],
                            'score': total_issue_score,
                            'context': issue_context[:5],  # Include up to 5 context samples
                            'confidence': min(1.0, total_issue_score / 10)  # Normalize confidence to 0-1
                        })
        
        # Extract key entities (like addresses, phone numbers, etc.)
        key_entities = {}
        for doc in documents:
            metadata = doc.doc_metadata or {}
            for entity_type in ['addresses', 'phone_numbers', 'email_addresses']:
                if entity_type not in key_entities:
                    key_entities[entity_type] = []
                key_entities[entity_type].extend(metadata.get(entity_type, []))
        
        # Remove duplicates
        for entity_type in key_entities:
            key_entities[entity_type] = list(set(key_entities[entity_type]))
        
        # Create enhanced analysis result
        analysis = {
            'case_id': case.id,
            'category_scores': category_scores,
            'detected_issues': sorted(detected_issues, key=lambda x: x['score'], reverse=True),
            'key_entities': key_entities,
            'dates': list(set(all_dates)),
            'names': list(set(all_names)),
            'weighted_document_count': len(weighted_docs),
            'primary_category': sorted_categories[0][0] if sorted_categories else None,
            'ai_insights': ai_insights if ai_insights else {},
            'analysis_method': 'ai_enhanced' if use_ai_enhanced_analysis else 'rule_based'
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
            'names': [],
            'analysis_method': 'fallback',
            'error': str(e)
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
        # Check if we have AI insights for more accurate merit scoring
        if analysis.get('analysis_method') == 'ai_enhanced' and 'ai_insights' in analysis:
            ai_insights = analysis.get('ai_insights', {})
            case_assessment = ai_insights.get('case_assessment', {})
            
            # If AI has already provided a merit score, use it with some adjustments
            if case_assessment and 'merit_score' in case_assessment:
                ai_score = float(case_assessment.get('merit_score', 0.0))
                
                # Make sure it's in range 0-1
                normalized_ai_score = max(0.0, min(1.0, ai_score))
                
                # We'll still check some facts to adjust the AI score slightly
                document_count = analysis.get('weighted_document_count', 0)
                entity_count = sum(len(entities) for entity_type, entities in analysis.get('key_entities', {}).items())
                
                # Apply small adjustments based on document and entity count
                # If there are very few documents or entities, slightly reduce the score
                if document_count < 2:
                    normalized_ai_score = normalized_ai_score * 0.9
                if entity_count < 3:
                    normalized_ai_score = normalized_ai_score * 0.95
                
                return round(normalized_ai_score, 2)
        
        # Enhanced rule-based merit scoring if AI score not available
        # Base factors for merit calculation with weighted importance
        evidence_strength = 0.0  # How much evidence is available (25%)
        issue_clarity = 0.0      # How clearly defined the legal issues are (35%)
        entity_completeness = 0.0 # How complete the key entities are (20%)
        document_quality = 0.0   # Quality of the documents provided (20%)
        
        # 1. Evidence strength - weighted by document count and type
        entity_count = sum(len(entities) for entity_type, entities in analysis.get('key_entities', {}).items())
        date_count = len(analysis.get('dates', []))
        name_count = len(analysis.get('names', []))
        
        # More entities and more varied entities = stronger evidence
        evidence_variety = len([et for et, entities in analysis.get('key_entities', {}).items() if entities])
        evidence_strength = min(0.25, ((entity_count / 20) * 0.15 + (evidence_variety / 3) * 0.1))
        
        # 2. Issue clarity - weighted by detected issues and their confidence
        detected_issues = analysis.get('detected_issues', [])
        if detected_issues:
            # Get top issues and their confidence scores
            top_issues = detected_issues[:3]
            
            # Calculate average confidence and weight by number of detected issues
            if 'confidence' in top_issues[0]:
                avg_confidence = sum(issue.get('confidence', 0) for issue in top_issues) / len(top_issues)
                issue_count_factor = min(1.0, len(detected_issues) / 3)
                issue_clarity = min(0.35, avg_confidence * 0.25 + issue_count_factor * 0.1)
            else:
                # Fallback if confidence not available
                top_issue_score = top_issues[0].get('score', 0)
                issue_clarity = min(0.35, top_issue_score / 15)
        
        # 3. Entity completeness - checks for presence of essential legal elements
        has_addresses = len(analysis.get('key_entities', {}).get('addresses', [])) > 0
        has_names = len(analysis.get('names', [])) > 0
        has_dates = len(analysis.get('dates', [])) > 0
        has_contacts = len(analysis.get('key_entities', {}).get('phone_numbers', [])) > 0 or len(analysis.get('key_entities', {}).get('email_addresses', [])) > 0
        
        # Weight different entity types by importance
        entity_completeness = (
            (has_addresses * 0.07) + 
            (has_names * 0.06) + 
            (has_dates * 0.05) + 
            (has_contacts * 0.02)
        )
        
        # 4. Document quality - based on weighted document count and primary category strength
        document_count = analysis.get('weighted_document_count', 0)
        
        # Get primary category score normalized against max possible
        category_scores = analysis.get('category_scores', {})
        if category_scores:
            primary_category = analysis.get('primary_category')
            primary_score = category_scores.get(primary_category, 0)
            max_possible_score = 100  # Approximate max score for a very clear case
            category_strength = min(1.0, primary_score / max_possible_score)
            
            # Combine document count (up to 5 docs) with category strength
            document_quality = min(0.2, (min(document_count, 5) / 5) * 0.1 + category_strength * 0.1)
        
        # Calculate final merit score with component weighting
        merit_score = evidence_strength + issue_clarity + entity_completeness + document_quality
        
        # Add weighted insights from context if available
        if 'context' in detected_issues[0] if detected_issues else False:
            context_confidence = len(detected_issues[0].get('context', [])) / 5  # Normalize to 5 contexts max
            merit_score += context_confidence * 0.05
        
        # Ensure score is between 0.0-1.0
        normalized_score = max(0.0, min(1.0, merit_score))
        
        # Map very low scores to at least 0.15 if any issues detected
        if normalized_score < 0.15 and detected_issues:
            normalized_score = 0.15
        
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
        list: Recommended forms with relevance scores
    """
    try:
        recommended_forms = []
        
        # Check if we have AI insights for form recommendations
        has_ai_insights = False
        ai_suggested_forms = []
        
        if analysis.get('analysis_method') == 'ai_enhanced' and 'ai_insights' in analysis:
            ai_insights = analysis.get('ai_insights', {})
            suggested_actions = ai_insights.get('suggested_actions', [])
            
            # If AI has made form recommendations, use them with high confidence
            if suggested_actions:
                has_ai_insights = True
                
                for action in suggested_actions:
                    form_name = action.get('form_name', '')
                    form_description = action.get('description', '')
                    form_relevance = action.get('relevance', 0.8)  # Default high relevance for AI suggestions
                    
                    # Try to match with our known forms
                    matched = False
                    for cat_key, cat_data in LEGAL_CATEGORIES.items():
                        for form_key, form_data in cat_data['forms'].items():
                            # Check if form names are similar (case insensitive partial match)
                            if form_name.lower() in form_data['name'].lower() or form_data['name'].lower() in form_name.lower():
                                matched = True
                                ai_suggested_forms.append({
                                    'id': f"{cat_key}_{form_key}",
                                    'name': form_data['name'],
                                    'description': form_data['description'],
                                    'category': cat_key,
                                    'score': float(form_relevance) * 100,  # Scale to match our scoring
                                    'ai_recommended': True
                                })
                                break
                        if matched:
                            break
                    
                    # If no match found, add as custom form
                    if not matched and form_name:
                        # Create a custom form ID based on the name
                        custom_id = "custom_" + re.sub(r'[^a-z0-9_]', '', form_name.lower().replace(' ', '_'))
                        ai_suggested_forms.append({
                            'id': custom_id,
                            'name': form_name,
                            'description': form_description or f"AI-recommended form for your {category} case",
                            'category': category,
                            'score': float(form_relevance) * 100,  # Scale to match our scoring
                            'ai_recommended': True,
                            'custom': True
                        })
        
        # Process rule-based detected issues
        detected_issues = analysis.get('detected_issues', [])
        
        # If we have detected issues, use those forms
        if detected_issues:
            for issue in detected_issues:
                form_category = issue.get('category')
                issue_type = issue.get('issue_type')
                
                if form_category and issue_type and form_category in LEGAL_CATEGORIES:
                    form_data = LEGAL_CATEGORIES[form_category]['forms'].get(issue_type)
                    if form_data:
                        # Check if this form was already recommended by AI
                        form_id = f"{form_category}_{issue_type}"
                        if not any(form['id'] == form_id for form in ai_suggested_forms):
                            recommended_forms.append({
                                'id': form_id,
                                'name': form_data['name'],
                                'description': form_data['description'],
                                'category': form_category,
                                'score': issue.get('score', 0),
                                'confidence': issue.get('confidence', issue.get('score', 0) / 10)
                            })
        
        # Combine AI suggestions with rule-based suggestions
        recommended_forms.extend(ai_suggested_forms)
        
        # If no issues detected or if the category doesn't match detected issues,
        # recommend general forms for the specified category
        if not recommended_forms or all(form['category'] != category for form in recommended_forms):
            if category in LEGAL_CATEGORIES:
                for issue_type, form_data in LEGAL_CATEGORIES[category]['forms'].items():
                    form_id = f"{category}_{issue_type}"
                    # Check if already added
                    if not any(form['id'] == form_id for form in recommended_forms):
                        recommended_forms.append({
                            'id': form_id,
                            'name': form_data['name'],
                            'description': form_data['description'],
                            'category': category,
                            'score': 0,  # Default score
                            'fallback': True  # Flag as fallback option
                        })
        
        # Add context to form recommendations if available
        for form in recommended_forms:
            # Find matching issue to get context if available
            for issue in detected_issues:
                if issue.get('issue_type') == form.get('id').split('_')[1]:
                    if 'context' in issue:
                        form['context_samples'] = issue.get('context', [])
                        break
        
        # Sort by score (highest first)
        recommended_forms = sorted(recommended_forms, key=lambda x: x.get('score', 0), reverse=True)
        
        # Add explanations for why each form is recommended
        for form in recommended_forms:
            if form.get('ai_recommended'):
                form['recommendation_reason'] = "Recommended by AI analysis based on document content"
            elif form.get('confidence', 0) > 0.7:
                form['recommendation_reason'] = "Strongly indicated by multiple evidence in your documents"
            elif form.get('confidence', 0) > 0.4:
                form['recommendation_reason'] = "Moderately indicated by evidence in your documents"
            elif form.get('fallback'):
                form['recommendation_reason'] = "Standard form for this category of legal issue"
            else:
                form['recommendation_reason'] = "Potentially relevant based on document analysis"
        
        return recommended_forms
    except Exception as e:
        logger.error(f"Error getting recommended forms: {str(e)}")
        return []

def get_relevant_precedents(category, analysis):
    """
    Get relevant legal precedents based on category and analysis using enhanced CanLII API
    
    Args:
        category: Legal category
        analysis: Dict containing case analysis
        
    Returns:
        dict: Enhanced precedent analysis with categorized precedents
    """
    try:
        # Import the CanLII API functions
        from utils.canlii_api import get_relevant_precedents as canlii_get_precedents
        
        # Determine the appropriate jurisdiction based on the case
        # Default to Ontario, but could be expanded to detect other provinces
        jurisdiction = 'on'  # Ontario
        
        # Get detected issues and facts for context-aware precedent matching
        detected_issues = analysis.get('detected_issues', [])
        names = analysis.get('names', [])
        key_entities = analysis.get('key_entities', {})
        
        # Enhance the analysis with key dates if available
        dates = analysis.get('dates', [])
        if dates:
            # Sort dates and find the most recent ones, which are likely more relevant
            dates = sorted(dates)[-3:]
        
        # Log the precedent search
        logger.info(f"Searching for precedents in category: {category}")
        if detected_issues:
            logger.info(f"With {len(detected_issues)} detected issues")
        
        # Call the enhanced CanLII API function for relevant precedents
        precedent_results = canlii_get_precedents(category, analysis, jurisdiction)
        
        # Additional processing for the UI display
        processed_results = {
            'top_precedents': [],
            'precedent_by_topic': {},
            'recent_developments': [],
            'landmark_cases': []
        }
        
        # Process the full search results into a UI-friendly format
        
        # 1. Extract top precedents across all categories
        all_cases = []
        
        # Add landmark cases
        if 'landmark_cases' in precedent_results:
            for case in precedent_results['landmark_cases']:
                processed_case = {
                    'title': case.get('title', ''),
                    'citation': case.get('citation', ''),
                    'snippet': case.get('snippet', ''),
                    'url': case.get('url', ''),
                    'relevance': case.get('relevance', 0.0),
                    'type': 'landmark',
                    'date': case.get('date', '')
                }
                all_cases.append(processed_case)
                processed_results['landmark_cases'].append(processed_case)
        
        # Add recent cases
        if 'recent_cases' in precedent_results:
            for case in precedent_results['recent_cases']:
                processed_case = {
                    'title': case.get('title', ''),
                    'citation': case.get('citation', ''),
                    'snippet': case.get('snippet', ''),
                    'url': case.get('url', ''),
                    'relevance': case.get('relevance', 0.0),
                    'type': 'recent',
                    'date': case.get('date', '')
                }
                all_cases.append(processed_case)
                processed_results['recent_developments'].append(processed_case)
        
        # Add topic-specific cases
        if 'topic_specific_cases' in precedent_results:
            for topic, cases in precedent_results['topic_specific_cases'].items():
                topic_cases = []
                for case in cases:
                    processed_case = {
                        'title': case.get('title', ''),
                        'citation': case.get('citation', ''),
                        'snippet': case.get('snippet', ''),
                        'url': case.get('url', ''),
                        'relevance': case.get('relevance', 0.0),
                        'type': 'topic',
                        'topic': topic,
                        'date': case.get('date', '')
                    }
                    all_cases.append(processed_case)
                    topic_cases.append(processed_case)
                
                if topic_cases:
                    processed_results['precedent_by_topic'][topic] = topic_cases
        
        # Add legislation-specific cases
        if 'legislation_cases' in precedent_results:
            for legislation, cases in precedent_results['legislation_cases'].items():
                legislation_cases = []
                for case in cases:
                    processed_case = {
                        'title': case.get('title', ''),
                        'citation': case.get('citation', ''),
                        'snippet': case.get('snippet', ''),
                        'url': case.get('url', ''),
                        'relevance': case.get('relevance', 0.0),
                        'type': 'legislation',
                        'legislation': legislation,
                        'date': case.get('date', '')
                    }
                    all_cases.append(processed_case)
                    legislation_cases.append(processed_case)
                
                if legislation_cases:
                    if 'legislation' not in processed_results['precedent_by_topic']:
                        processed_results['precedent_by_topic']['legislation'] = []
                    processed_results['precedent_by_topic']['legislation'].extend(legislation_cases)
        
        # Sort all cases by relevance and select top cases
        all_cases = sorted(all_cases, key=lambda x: x.get('relevance', 0), reverse=True)
        processed_results['top_precedents'] = all_cases[:5]  # Top 5 most relevant cases
        
        # Add metadata and insights
        processed_results['metadata'] = {
            'category': category,
            'jurisdiction': jurisdiction,
            'issue_count': len(detected_issues),
            'search_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        # If we have analysis data, add insights about the precedent relevance
        if detected_issues:
            issue_insights = []
            for issue in detected_issues:
                if issue.get('confidence', 0) > 0.6:  # Only include higher confidence issues
                    issue_insights.append({
                        'issue_type': issue.get('issue_type', ''),
                        'confidence': issue.get('confidence', 0),
                        'relevant_precedents': [c for c in all_cases 
                                               if issue.get('issue_type', '') in c.get('snippet', '').lower()][:2]
                    })
            
            if issue_insights:
                processed_results['issue_insights'] = issue_insights
        
        return processed_results
    except Exception as e:
        logger.error(f"Error getting relevant precedents: {str(e)}")
        # Fall back to a simplified structure if there's an error
        return {
            'top_precedents': [],
            'precedent_by_topic': {},
            'recent_developments': [],
            'landmark_cases': [],
            'error': str(e)
        }
