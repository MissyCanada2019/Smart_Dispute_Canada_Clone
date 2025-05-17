from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from src.models import db, Case, Evidence, Payment
from src.server.ai_helpers import extract_text_from_file, classify_legal_issue, score_merit, select_form
import os

main = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    cases = Case.query.filter_by(user_id=current_user.id).all()

    if request.method == "POST":
        case_id = request.form.get("case_id")
        file = request.files.get("document")
        tag = request.form.get("tag")
        notes = request.form.get("notes")

        if not case_id or not file or not allowed_file(file.filename):
            flash("Please select a valid case and upload a valid document.", "danger")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
        user_folder = os.path.join(upload_folder, str(current_user.id))
        os.makedirs(user_folder, exist_ok=True)
        save_path = os.path.join(user_folder, filename)
        file.save(save_path)

        evidence = Evidence(
            case_id=case_id,
            user_id=current_user.id,
            filename=filename,
            file_path=save_path,
            tag=tag
        )
        db.session.add(evidence)
        db.session.commit()

        text, _ = extract_text_from_file(save_path)
        legal_issue = classify_legal_issue(text)
        merit_score = score_merit(text, legal_issue)
        form_info = select_form(legal_issue, current_user.province)

        case = Case.query.get(case_id)
        case.legal_issue = legal_issue
        case.confidence_score = merit_score
        db.session.commit()

        return render_template("review_case.html", case=case, form_info=form_info, merit_score=merit_score, explanation="This is your AI-generated summary.")

    return render_template("upload.html", cases=cases)

@main.route("/review_case/<int:case_id>")
@login_required
def review_case(case_id):
    case = Case.query.get_or_404(case_id)
    if case.user_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("main.upload"))

    form_info = select_form(case.legal_issue or "", current_user.province)
    explanation = "AI confidence and form suggestions based on your evidence."
    return render_template("review_case.html", case=case, form_info=form_info, merit_score=case.confidence_score or 0, explanation=explanation)

@main.route("/confirm_payment/<int:case_id>", methods=["POST"])
@login_required
def confirm_payment(case_id):
    case = Case.query.get_or_404(case_id)

    if case.user_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("main.upload"))

    case.is_paid = True
    db.session.commit()

    payment = Payment(
        user_id=current_user.id,
        case_id=case.id,
        amount=9.99,
        payment_type='legal_package',
        payment_method='e-transfer',
        status='confirmed'
    )
    db.session.add(payment)
    db.session.commit()

    flash("Payment confirmed. You can now download your legal package.", "success")
    return redirect(url_for("main.review_case", case_id=case.id))

@main.route("/download_legal_package/<int:case_id>")
@login_required
def download_legal_package(case_id):
    case = Case.query.get_or_404(case_id)

    if case.user_id != current_user.id or not case.is_paid:
        flash("You must complete payment to access this document.", "warning")
        return redirect(url_for("main.review_case", case_id=case.id))

    package_path = os.path.join(current_app.root_path, "legal_packages", f"case_{case_id}_package.pdf")

    if not os.path.exists(package_path):
        flash("Legal package not ready yet. Please check back soon.", "danger")
        return redirect(url_for("main.review_case", case_id=case.id))

    return send_file(package_path, as_attachment=True)
