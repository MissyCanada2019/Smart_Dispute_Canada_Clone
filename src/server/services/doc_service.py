from flask import Blueprint, send_file, redirect, url_for, flash
from flask_login import login_required, current_user
from src.models import Case
from src.server.doc_generator import generate_docx  # your actual generator path

doc_bp = Blueprint("doc", __name__)

@doc_bp.route("/generate/<int:case_id>")
@login_required
def generate_document(case_id):
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first()
    if not case:
        flash("Access denied or case not found.", "danger")
        return redirect(url_for("main.dashboard"))

    try:
        docx_path = generate_docx(case, current_user)
        return send_file(docx_path, as_attachment=True)
    except FileNotFoundError as e:
        flash(str(e), "danger")
        return redirect(url_for("main.dashboard"))
