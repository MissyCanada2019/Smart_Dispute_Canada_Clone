import re

# Define legal categories and trigger keywords
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

def classify_legal_issue(text: str) -> dict:
    """
    Classify the legal issue based on the uploaded content.
    Returns a dictionary with category and matched keywords.
    """
    matched = {}
    for category, keywords in LEGAL_ISSUES.items():
        found = [kw for kw in keywords if re.search(rf"\b{re.escape(kw)}\b", text, re.IGNORECASE)]
        if found:
            matched[category] = found

    if matched:
        # Pick the category with the most matches
        best_match = max(matched.items(), key=lambda item: len(item[1]))
        return {
            "category": best_match[0],
            "matched_keywords": best_match[1],
            "confidence": len(best_match[1]) / len(LEGAL_ISSUES[best_match[0]])
        }
    else:
        return {
            "category": "unknown",
            "matched_keywords": [],
            "confidence": 0.0
        }
