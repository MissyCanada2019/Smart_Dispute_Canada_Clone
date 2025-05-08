# utils/merit_weight.py
import logging
import random

# Simulated scraping results from Canadian legal resources (replace with real query later)
SIMULATED_PRECEDENTS = {
    "Landlord-Tenant Dispute": {"win_rate": 0.76, "avg_award": 5000},
    "Credit Report Error": {"win_rate": 0.62, "avg_award": 1000},
    "Human Rights Complaint": {"win_rate": 0.51, "avg_award": 8000},
    "Small Claims": {"win_rate": 0.70, "avg_award": 2000},
    "Police Misconduct": {"win_rate": 0.43, "avg_award": 15000},
    "Child Protection (CAS)": {"win_rate": 0.55, "avg_award": 0},
}

PROVINCE_MODIFIERS = {
    "ON": 1.00,
    "BC": 1.05,
    "QC": 0.95,
    "AB": 0.90,
    "SK": 1.02,
    "NS": 1.01,
    "MB": 0.88
}


def query_canadian_case_stats(issue_category, province="ON"):
    """
    Simulates querying Canadian legal databases (CanLII, court websites, gov portals).
    Returns success rate (win%) and average damages from past similar cases.
    """
    base_data = SIMULATED_PRECEDENTS.get(issue_category, {"win_rate": 0.40, "avg_award": 1000})
    modifier = PROVINCE_MODIFIERS.get(province.upper(), 1.0)

    adjusted_win_rate = min(base_data["win_rate"] * modifier, 0.95)  # Cap at 95%
    return {
        "win_rate": round(adjusted_win_rate, 2),
        "avg_award": round(base_data["avg_award"] * modifier, 2)
    }


def score_merit(issues_detected, province="ON", matched_keywords=None):
    """
    Assigns a dynamic merit score based on issues, province, keyword strength,
    and mock Canadian precedent success rates.
    """
    total_score = 0
    total_weight = 0

    for issue in issues_detected:
        case_data = query_canadian_case_stats(issue, province)
        issue_score = case_data["win_rate"] * 100  # Convert to percentage
        total_score += issue_score
        total_weight += 1

    # Add keyword bonus
    if matched_keywords:
        keyword_boost = min(len(matched_keywords) * 1.5, 15)
    else:
        keyword_boost = 0

    # Final merit calculation
    base_avg = total_score / total_weight if total_weight else 30
    final_score = min(base_avg + keyword_boost, 100)

    return round(final_score, 2)
