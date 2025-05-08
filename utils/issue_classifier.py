# utils/issue_classifier.py

import re

# Example list of Canadian legal keywords mapped to categories
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
    "child protection": "Child Protection (CAS)"
}


def extract_legal_issues(text):
    """
    Scan document text for legal keywords and return a set of issues.

    Args:
        text (str): Full OCR'd or uploaded document text.

    Returns:
        set: Set of detected legal issue categories (strings).
    """
    detected_issues = set()

    cleaned_text = re.sub(r'[^\w\s]', '', text.lower())

    for keyword, category in LEGAL_ISSUE_KEYWORDS.items():
        if keyword in cleaned_text:
            detected_issues.add(category)

    return detected_issues
