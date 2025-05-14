import json
import os
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from src.models import Case, Evidence

legal_help_bp = Blueprint("legal_help", __name__)

@legal_help_bp.route("/legal-help/<int:case_id>")
@login_required
def show_legal_help(case_id):
    case = Case.query.get_or_404(case_id)

    # For now, assume case.description contains the issue type
    legal_issue = case.description.lower()  # Ideally you'd use classify_legal_issue()

    # Load scraped legal data
    try:
        with open("scraped_data/steps_to_justice.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    # Filter entries relevant to the issue
    matching_entries = [
        entry for entry in data
        if legal_issue in entry["question"].lower() or legal_issue in entry["answer"].lower()
    ]

    return render_template("legal_help.html", case=case, results=matching_entries)
