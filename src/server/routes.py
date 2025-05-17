from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os

from src.models import db, Case, Evidence
from src.server.utils.ocr import extract_text_from_file
from src.server.utils.issue_classifier import classify_legal_issue
from src.server.utils.merit_weight import score_merit
from src.server.utils.form_selector import select_form

main = Blueprint("main", __name__)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    cases = Case.query.filter_by(user_id=current_user.id).all()
    if request.method == "POST":
        case_id = request.form["case_id"]
        file = request.files.get("document")
        tag = request.form.get("tag")

        if not file or not allowed_file(file.filename):
            flash("Invalid file type.", "danger")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        user_folder = os.path.join(current_app.config["UPLOAD_FOLDER"], str(current_user.id))
        os.makedirs(user_folder, exist_ok=True)
        file_path = os.path.join(user_folder, filename)
        file.save(file_path)

        # Save to DB
        evidence = Evidence(
            case_id=case_id,
            user_id=current_user.id,
            filename=filename,
            file_path=file_path,
            tag=tag
        )
        db.session.add(evidence)

        # AI Analysis
        text, _ = extract_text_from_file(file_path)
        legal_issue = classify_legal_issue(text)
        confidence = score_merit(text, legal_issue)
        form = select_form(legal_issue, current_user.province)

        # Update Case
        case = Case.query.get(case_id)
        case.legal_issue = legal_issue
        case.confidence_score = confidence
        db.session.commit()

        flash(
            f"File uploaded. Case scored {confidence:.1f}% merit. Suggested form: {form}.",
            "success"
        )
        return redirect(url_for('main.review_case', case_id=case_id))

    return render_template("upload.html", cases=cases)
