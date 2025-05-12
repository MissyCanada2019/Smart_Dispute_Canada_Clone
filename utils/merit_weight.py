import re
import logging
import random

# Simulated Canadian case precedent stats
SIMULATED_PRECEDENTS = {
    "Landlord-Tenant Dispute": {"win_rate": 0.76, "avg_award": 5000},
    "Credit Report Error": {"win_rate": 0.62, "avg_award": 1000},
    "Human Rights Complaint": {"win_rate": 0.51, "avg_award": 8000},
    "Small Claims": {"win_rate": 0.70, "avg_award": 2000},
    "Police Misconduct": {"win_rate": 0.43, "avg_award": 15000},
    "Child Protection (CAS)": {"win_rate": 0.55, "avg_award": 0},
}

PROVINCE_MODIFIERS = {
    "ON": 1.00, "BC": 1.05, "QC": 0.95, "AB": 0.90,
    "SK": 1.02, "NS": 1.01, "MB": 0.88
}

LEGAL_TERMS = [
    "eviction", "contract", "termination", "lease", "notice", "agreement",
    "claim", "human rights", "discrimination", "negligence", "damages", "compensation"
]

# Direct keyword scoring
def calculate_text_score(text):
    score = 0
    reasons = []

    text_lower = text.lower()

    # Legal terms match
    hits = sum(1 for term in LEGAL_TERMS if term in text_lower)
    if hits >= 3:
        score += 25
        reasons.append("Relevant legal terms found")

    # Dates
    if re.search(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', text):
        score += 10
        reasons.append("Date(s) present")

    # Names
    if re.search(r'\b[A-Z][a-z]+\s[A-Z][a-z]+\b', text):
        score += 10
        reasons.append("Full names found")

    # Addresses
    if re.search(r'\d{1,5}\s\w+\s(?:Street|St|Avenue|Ave|Rd|Road|Blvd|Drive|Dr)\b', text, re.IGNORECASE):
        score += 10
        reasons.append("Address present")

    # Supporting docs
    if "photo" in text_lower or "screenshot" in text_lower or "attachment" in text_lower:
        score += 15
        reasons.append("Mention of supporting evidence")

    # Length bonus
    if len(text.split()) >= 150:
        score += 30
        reasons.append("Sufficient document length")

    return min(score, 100), reasons, hits

# Simulate pulling precedent stats
def query_canadian_case_stats(issue_category, province="ON"):
    base_data = SIMULATED_PRECEDENTS.get(issue_category, {"win_rate": 0.40, "avg_award": 1000})
    modifier = PROVINCE_MODIFIERS.get(province.upper(), 1.0)
    adjusted_win_rate = min(base_data["win_rate"] * modifier, 0.95)
    return {
        "win_rate": round(adjusted_win_rate, 2),
        "avg_award": round(base_data["avg_award"] * modifier, 2)
    }

# Final merit score combining both techniques
def score_merit(text, issue_category="General", province="ON"):
    text_score, reasons, keyword_hits = calculate_text_score(text)
    precedent = query_canadian_case_stats(issue_category, province)
    precedent_score = precedent["win_rate"] * 100

    # Balance weight: 60% text, 40% precedent
    final_score = round((text_score * 0.6) + (precedent_score * 0.4), 2)

    return {
        "merit_score": final_score,
        "reasons": reasons,
        "keyword_hits": keyword_hits,
        "win_rate": precedent["win_rate"],
        "avg_award": precedent["avg_award"],
        "precedent_used": issue_category
    }
