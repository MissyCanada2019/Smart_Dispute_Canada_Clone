import os
import io
import zipfile
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from server.models import db, Case, Evidence, Payment
from utils.ocr import process_document
from utils.issue_classifier import extract_legal_issues
from utils.merit_weight import score_merit
from utils.document_generator import generate_legal_form

routes = Blueprint("routes", __name__)

@routes.route("/create-case", methods=["GET", "POST"])
@login_required
def create_case():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form.get("description")
        new_case = Case(user_id=current_user.id, title=title, description=description)
        db.session.add(new_case)
        db.session.commit()
        flash("Case created successfully!", "success")
        return redirect(url_for("routes.dashboard"))
    return render_template("create_case.html")

@routes.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    cases = Case.query.filter_by(user_id=current_user.id).all()
    if request.method == "POST":
        file = request.files["document"]
        case_id = request.form["case_id"]
        tag = request.form.get("tag", "")

        if file:
            filename = secure_filename(file.filename)
            upload_path = os.path.join("uploads", filename)
            file.save(upload_path)

            evidence = Evidence(
                user_id=current_user.id,
                case_id=case_id,
                filename=filename,
                file_path=upload_path,
                tag=tag
            )
            db.session.add(evidence)
            db.session.commit()
            flash("Evidence uploaded successfully.", "success")
            return redirect(url_for("routes.dashboard"))

    return render_template("uploads.html", cases=cases)

@routes.route("/dashboard")
@login_required
def dashboard():
    user_cases = Case.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", cases=user_cases)

@routes.route("/generate-legal-package/<int:case_id>")
@login_required
def generate_legal_package(case_id):
    case = Case.query.get_or_404(case_id)
    if case.user_id != current_user.id:
        flash("Unauthorized access", "danger")
        return redirect(url_for("routes.dashboard"))

    paid = Payment.query.filter_by(case_id=case.id, status="completed").first()
    if not paid and current_user.subscription_type != "unlimited":
        return redirect(url_for("routes.pay_for_case", case_id=case.id))

    combined_text = ""
    for ev in case.evidence:
        text, _ = process_document(ev.file_path, ev.filename.split(".")[-1])
        combined_text += text + "\n"

    issues = extract_legal_issues(combined_text)
    merit_score = score_merit(issues, province=current_user.province)

    form_path = f"generated_forms/case_{case.id}_form.docx"
    generate_legal_form("templates/forms/base_form.docx", form_path, {
        "FULL_NAME": current_user.full_name,
        "ADDRESS": current_user.address,
        "PHONE": current_user.phone,
        "POSTAL_CODE": current_user.postal_code,
        "PROVINCE": current_user.province,
        "CASE_TITLE": case.title
    })

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
        zipf.write(form_path, os.path.basename(form_path))
        for ev in case.evidence:
            zipf.write(ev.file_path, os.path.basename(ev.file_path))
    zip_buffer.seek(0)

    flash(f"Merit Score: {merit_score:.2f}%", "info")
    return send_file(zip_buffer, mimetype="application/zip",
                     download_name=f"SmartDispute_Case_{case.title}.zip", as_attachment=True)

@routes.route("/pay/<int:case_id>")
@login_required
def pay_for_case(case_id):
    case = Case.query.get_or_404(case_id)
    if case.user_id != current_user.id:
        flash("Unauthorized access", "danger")
        return redirect(url_for("routes.dashboard"))

    paid = Payment.query.filter_by(case_id=case.id, status="completed").first()
    if paid or current_user.subscription_type == "unlimited":
        flash("Payment already completed.", "info")
        return redirect(url_for("routes.generate_legal_package", case_id=case.id))

    return render_template("pay_etf.html", case=case)

def register_routes(app):
    app.register_blueprint(routes)
