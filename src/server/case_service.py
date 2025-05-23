import random
from src.models import Case, Evidence
from datetime import datetime

def score_case_merit(case):
    # Get evidence
    evidence_list = Evidence.query.filter_by(case_id=case.id).all()

    # Basic scoring logic (placeholder — refine later)
    score = 50  # Base score

    if case.legal_issue:
        issue = case.legal_issue.lower()
        if "eviction" in issue or "repair" in issue:
            score += 15
        if "discrimination" in issue:
            score += 10
        if "harassment" in issue:
            score += 5

    if evidence_list:
        score += len(evidence_list) * 5
    else:
        score -= 20

    score = min(100, max(1, score))  # Keep between 1 and 100
    return score

def classify_venue(case):
    """Return which legal venue the case likely belongs to"""
    issue = (case.legal_issue or "").lower()

    if "eviction" in issue or "tenant" in issue or "repair" in issue:
        return "Landlord and Tenant Board (LTB)"
    elif "discrimination" in issue:
        return "Human Rights Tribunal of Ontario (HRTO)"
    elif "credit" in issue or "debt" in issue:
        return "Consumer Protection (Small Claims Court)"
    elif "contract" in issue or "damages" in issue:
        return "Small Claims Court"
    else:
        return "Needs Review"
