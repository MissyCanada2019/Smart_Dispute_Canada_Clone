import re

# Example keyword maps (expand this later for better accuracy)
LEGAL_ISSUE_KEYWORDS = {
    "tenant": ["landlord", "eviction", "rent", "lease", "repairs", "LTB"],
    "family": ["custody", "divorce", "child support", "spousal", "parenting"],
    "employment": ["wrongful dismissal", "severance", "contract", "harassment", "fired"],
    "human_rights": ["discrimination", "racism", "accommodation", "disability", "bias"],
    "credit": ["equifax", "transunion", "credit report", "inquiry", "debt", "collections"],
    "small_claims": ["breach", "contract", "damage", "unpaid", "refund"],
    "criminal": ["theft", "assault", "charges", "police", "arrest", "bail"]
}

PROVINCE_RULES = {
    "ON": {
        "tenant": "Landlord and Tenant Board",
        "family": "Ontario Family Court",
        "employment": "Ontario Labour Relations Board",
        "human_rights": "Ontario Human Rights Tribunal"
    },
    "BC": {
        "tenant": "BC Residential Tenancy Branch",
        "family": "BC Family Court",
        "employment": "WorkSafeBC / Labour Relations Board",
        "human_rights": "BC Human Rights Tribunal"
    },
    # Add more provinces here as needed
}

def classify_legal_issue(text, province="ON"):
    text = text.lower()
    match_scores = {}

    for issue, keywords in LEGAL_ISSUE_KEYWORDS.items():
        count = sum(1 for word in keywords if word in text)
        match_scores[issue] = count

    # Determine best match
    top_issue = max(match_scores, key=match_scores.get)
    confidence = round((match_scores[top_issue] / max(len(LEGAL_ISSUE_KEYWORDS[top_issue]), 1)) * 100)

    # Determine where to file (if known)
    filing_body = PROVINCE_RULES.get(province.upper(), {}).get(top_issue, "General Civil Court")

    return f"{top_issue.replace('_', ' ').title()} ({filing_body})", confidence
