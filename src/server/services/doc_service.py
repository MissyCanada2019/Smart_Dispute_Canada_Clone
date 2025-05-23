# src/server/services/doc_service.py

from src.server.doc_generator import generate_docx  # or your docx generation logic

def get_download_path(case, user):
    # Returns path to generated .docx file
    return generate_docx(case, user)

def get_preview_path(case, user):
    # Optionally implement PDF preview logic if needed
    return generate_docx(case, user)  # or generate_preview(case, user)
