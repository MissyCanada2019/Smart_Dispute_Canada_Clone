import re

# Trigger terms for each legal issue category
LEGAL_ISSUES = {
    "landlord-tenant": [
        "eviction", "rent", "repair", "landlord", "lease", "N4", "maintenance", "bedbug", "mold", "housing"
    ],
    "credit": [
        "equifax", "transunion", "credit report", "collections", "dispute", "chargeoff", "fraudulent account"
    ],
    "human-rights": [
        "discrimination", "accommodation", "racism", "harassment", "mental health", "disabled", "bias"
    ],
    "small-claims": [
        "money owed", "contract", "invoice", "breach", "damage", "property", "refund"
    ],
    "child-protection": [
        "CAS", "Children’s Aid", "neglect", "abuse", "custody", "visit", "protection", "removal"
    ],
    "police": [
        "police", "arrest", "assault", "abuse of power", "oppression", "harassed", "badge", "violence"
    ]
}

def classify_legal_issue(text: str) -> tuple[str, list[str], float]:
    """
    Classifies the text into a legal category based on keyword matches.
    
    Returns:
        - category (str): the best-matching category
        - matched_keywords (list): keywords found in text
        - confidence (float): match strength from 0.0 to 1.0
    """
    matched = {}

    for category, keywords in LEGAL_ISSUES.items():
        found = [kw for kw in keywords if re.search(rf"\b{re.escape(kw)}\b", text, re.IGNORECASE)]
        if found:
            matched[category] = found

    if matched:
        best_category, hits = max(matched.items(), key=lambda item: len(item[1]))
        confidence = len(hits) / len(LEGAL_ISSUES[best_category])
        return best_category, hits, confidence

    return "unknown", [], 0.0
