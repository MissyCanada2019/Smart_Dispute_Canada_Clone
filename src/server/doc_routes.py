from flask import Blueprint, send_file, redirect, url_for, flash
from flask_login import login_required, current_user
from src.server.services.doc_service import get_download_path

doc_bp = Blueprint("doc", __name__)

@doc_bp.route("/generate/<int:case_id>")
@login_required
def generate_document(case_id):
    path, error = get_download_path(case_id, current_user)

    if error:
        flash(error, "danger")
        return redirect(url_for("main.dashboard"))

    return send_file(path, as_attachment=True)
