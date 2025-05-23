import os
from flask import send_file
from src.models import Case
from src.server.doc_generator import generate_docx

def get_download_path(case_id, user):
    """Generates the final DOCX document for a paid case and returns its path."""
    case = Case.query.filter_by(id=case_id, user_id=user.id).first()
    if not case:
        return None, "Access denied or case not found."

    if not case.is_paid:
        return None, "Payment required to download the document."

    try:
        docx_path = generate_docx(case, user)
        return docx_path, None
    except FileNotFoundError as e:
        return None, str(e)

def get_preview_path(case_id, user):
    """Generates a preview DOCX file for the case, without requiring payment."""
    case = Case.query.filter_by(id=case_id, user_id=user.id).first()
    if not case:
        return None, "Access denied or case not found."

    try:
        preview_path = generate_docx(case, user, preview=True)
        return preview_path, None
    except FileNotFoundError as e:
        return None, str(e)
