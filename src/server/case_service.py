from flask import current_app
from src.server.extensions import db
from src.models import Case
from src.server.merit_weight import score_merit


def handle_upload(form_data, user_id):
    new_case = Case(
        user_id=user_id,
        title=form_data.get("title", "Untitled Case"),
        description=form_data.get("description"),
        legal_issue=form_data.get("legal_issue"),
        matched_keywords=form_data.get("matched_keywords"),
        confidence_score=form_data.get("confidence_score"),
    )
    db.session.add(new_case)
    db.session.commit()
    return new_case


def prepare_review_data(case_id, user):
    case = Case.query.filter_by(id=case_id, user_id=user.id).first()
    if not case:
        return None, None, None, None, None

    # Generate merit score using the case description and category
    issue_category = case.legal_issue or "General"
    province = user.province or "ON"
    description = case.description or ""

    merit_result = score_merit(description, issue_category, province)

    merit_score = merit_result["merit_score"]
    explanation = f"""
    Score based on keyword detection, legal term density, and simulated Canadian precedent.
    Estimated win rate for {issue_category} in {province}: {merit_result['win_rate'] * 100:.0f}%
    """

    form_info = {
        "category": issue_category,
        "keywords": merit_result["keyword_hits"],
        "reasons": merit_result["reasons"],
        "avg_award": merit_result["avg_award"],
    }

    email = current_app.config.get("MAILGUN_FROM", "support@smartdispute.ai")

    return case, form_info, merit_score, explanation.strip(), email
