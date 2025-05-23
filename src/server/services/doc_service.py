from flask import send_file
from src.models import Case
from src.server.doc_generator import generate_docx

def get_download_path(case_id, user):
    case = Case.query.filter_by(id=case_id, user_id=user.id).first()
    if not case:
        return None, "Access denied or case not found."

    try:
        docx_path = generate_docx(case, user)
        return docx_path, None
    except FileNotFoundError as e:
        return None, str(e)
