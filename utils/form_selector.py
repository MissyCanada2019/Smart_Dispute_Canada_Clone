# utils/form_selector.py

import json
import os

def select_form(issue_type, province="ON"):
    issue_type = issue_type.lower()
    province = province.upper()

    # Step 1: Check static matches for tenant, family, etc.
    static_map = {
        "tenant": {"court": "Landlord and Tenant Board", "form_name": "LTB T2", "form_file": "ltb_t2.docx"},
        "human_rights": {"court": "Human Rights Tribunal", "form_name": "HRTO Form 1", "form_file": "hrto_form1.docx"},
        "credit": {"court": "Privacy Commission", "form_name": "Credit Dispute", "form_file": "credit_dispute.docx"},
    }

    for keyword in static_map:
        if keyword in issue_type:
            return static_map[keyword]

    # Step 2: Check scraped federal court forms
    try:
        with open("data/federal_forms.json", "r", encoding="utf-8") as f:
            federal_forms = json.load(f)
            for form in federal_forms:
                if issue_type in form["title"].lower():
                    return {
                        "court": form["court"],
                        "form_name": form["title"],
                        "form_file": form["url"],
                        "notes": "Scraped from Federal Court"
                    }
    except Exception as e:
        print(f"Could not load federal forms: {e}")

    # Default fallback
    return {
        "court": "General Civil Court",
        "form_name": "Generic Complaint",
        "form_file": "generic_complaint.docx"
    }
