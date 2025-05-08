# utils/issue_classifier.py

import re

# Base legal keywords mapped to categories
LEGAL_ISSUE_KEYWORDS = {
    "repair": "Landlord-Tenant Dispute",
    "maintenance": "Landlord-Tenant Dispute",
    "mold": "Landlord-Tenant Dispute",
    "eviction": "Landlord-Tenant Dispute",
    "n4 notice": "Landlord-Tenant Dispute",
    "credit": "Credit Report Error",
    "equifax": "Credit Report Error",
    "transunion": "Credit Report Error",
    "wrong account": "Credit Report Error",
    "human rights": "Human Rights Complaint",
    "discrimination": "Human Rights Complaint",
    "accommodation": "Human Rights Complaint",
    "rent": "Landlord-Tenant Dispute",
    "quiet enjoyment": "Landlord-Tenant Dispute",
    "small claims": "Small Claims",
    "damage": "Small Claims",
    "contract": "Small Claims",
    "refund": "Small Claims",
    "police": "Police Misconduct",
    "harassment": "Police Misconduct",
    "cas": "Child Protection (CAS)",
    "child protection": "Child Protection (CAS)",
}

# Province-specific legal triggers (can be expanded)
PROVINCE_ISSUE_TRIGGERS = {
    "ON": {  # Ontario
        "ltb": "Landlord-Tenant Dispute",
        "form n4": "Landlord-Tenant Dispute",
        "rta": "Landlord-Tenant Dispute",  # Residential Tenancies Act
        "hrto": "Human Rights Complaint",
        "form c": "Child Protection (CAS)"
    },
    "BC": {
        "rtb": "Landlord-Tenant Dispute",  # Residential Tenancy Branch
        "bc human rights": "Human Rights Complaint",
        "form g": "Child Protection (CAS)"
    },
    "AB": {
        "residential tenancies act": "Landlord-Tenant Dispute",
        "saform": "Child Protection (CAS)"
    },
    "QC": {
        "regie du logement": "Landlord-Tenant Dispute",
        "commission des droits": "Human Rights Complaint"
    },
    # Add more provinces and phrases here
}


def extract_legal_issues(text, province_code="ON"):
    """
    Scan document for general and province-specific keywords.

    Args:
        text (str): Full OCR or uploaded text.
        province_code (str): Province abbreviation like 'ON', 'BC', etc.

    Returns:
        dict: {
            'issues': set of issue categories,
            'form_triggers': list of strings (triggered forms),
            'keywords_found': list of matched keywords
        }
    """
    detected_issues = set()
    form_triggers = []
    keywords_found = []

    cleaned_text = re.sub(r'[^\w\s]', '', text.lower())

    # Base keyword matching
    for keyword, category in LEGAL_ISSUE_KEYWORDS.items():
        if keyword in cleaned_text:
            detected_issues.add(category)
            keywords_found.append(keyword)

    # Province-specific matching
    province_keywords = PROVINCE_ISSUE_TRIGGERS.get(province_code.upper(), {})
    for keyword, category in province_keywords.items():
        if keyword in cleaned_text:
            detected_issues.add(category)
            form_triggers.append(keyword)
            keywords_found.append(keyword)

    return {
        "issues": detected_issues,
        "form_triggers": form_triggers,
        "keywords_found": keywords_found
    }
