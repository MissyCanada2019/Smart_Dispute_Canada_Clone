from flask import current_app
from src.server.extensions import db

def handle_upload(form_data, user_id):
    from src.models import Case  # Delayed import to avoid circular import

    new_case = Case(
        user_id=user_id,
        case_type=form_data.get("case_type"),
        province=form_data.get("province"),
        facts=form_data.get("facts"),
        respondent=form_data.get("respondent"),
        violations=form_data.get("violations"),
    )
    db.session.add(new_case)
    db.session.commit()
    return new_case

def prepare_review_data(case_id):
    from src.models import Case  # Delayed import to avoid circular import

    case = Case.query.get(case_id)
    if not case:
        return None

    return {
        "case_id": case.id,
        "case_type": case.case_type,
        "province": case.province,
        "facts": case.facts,
        "respondent": case.respondent,
        "violations": case.violations,
    }
