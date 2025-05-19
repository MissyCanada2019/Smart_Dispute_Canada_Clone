from pathlib import Path

# Recreate case_service.py after code execution state reset
case_service_code = '''\
import os
from werkzeug.utils import secure_filename
from src.models import Case, Evidence, db
from src.server.ai_helpers import extract_text_from_file, classify_legal_issue, score_merit, select_form
from src.steps_scraper import run_scraper

UPLOAD_FOLDER = "uploads"

def handle_document_upload(user, file, title, description, tag):
    filename = secure_filename(file.filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file.save(save_path)

    text, _ = extract_text_from_file(save_path)
    legal_issue = classify_legal_issue(text)
    score = score_merit(text, legal_issue)
    keywords, form_info = select_form(legal_issue, user.province)

    run_scraper()  # Optional: pass legal_issue later

    new_case = Case(
        user_id=user.id,
        title=title,
        description=description,
        legal_issue=legal_issue,
        confidence_score=score,
        matched_keywords=keywords,
        is_paid=False
    )
    db.session.add(new_case)
    db.session.commit()

    evidence = Evidence(
        user_id=user.id,
        case_id=new_case.id,
        filename=filename,
        file_path=save_path,
        tag=tag
    )
    db.session.add(evidence)
    db.session.commit()

    return new_case
'''

case_service_path = Path("src/services/case_service.py")
case_service_path.parent.mkdir(parents=True, exist_ok=True)
case_service_path.write_text(case_service_code)
