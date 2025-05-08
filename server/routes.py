import os
import io
import zipfile
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, make_response
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from weasyprint import HTML

from server.models import db, Case, Evidence, Payment
from utils.ocr import process_document
from utils.issue_classifier import extract_legal_issues
from utils.merit_weight import score_merit
from utils.document_generator import generate_legal_form

routes = Blueprint("routes", __name__)

# --- Homepage ---
@routes.route("/")
def home():
    return render_template("index.html")

# --- Case Creation ---
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

# --- Upload Evidence ---
@routes.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    cases = Case.query.filter_by(user_id=current_user.id).all()
    if request.method == "POST":
        uploaded_file = request.files["document"]
        case_id = request.form["case_id"]
        tag = request.form.get("tag", "")
        if uploaded_file:
            filename = secure_filename(uploaded_file.filename)
            upload_path = os.path.join("uploads", filename)
            uploaded_file.save(upload_path)

            new_evidence = Evidence(
                user_id=current_user.id,
                case_id=case_id,
                filename=filename,
                file_path=upload_path,
                tag=tag
            )
            db.session.add(new_evidence)
            db.session.commit()
            flash("Evidence uploaded successfully.", "success")
            return redirect(url_for("routes.dashboard"))
    return render_template("upload.html", cases=cases)

# --- Dashboard (example placeholder) ---
@routes.route("/dashboard")
@login_required
def dashboard():
    cases = Case.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", cases=cases)

# --- Generate Legal Package ---
@routes.route("/generate-legal-package/<int:case_id>")
@login_required
def generate_legal_package(case_id):
    case = Case.query.get_or_404(case_id)
    if case.user_id != current_user.id:
        flash("Unauthorized", "danger")
        return redirect(url_for("routes.dashboard"))

    paid = Payment.query.filter_by(case_id=case_id, status="completed").first()
    if not paid and current_user.subscription_type != "unlimited":
        return redirect(url_for("routes.pay_for_case", case_id=case.id))

    combined_text = ""
    for ev in case.evidence:
        text, _ = process_document(ev.file_path, ev.filename.split(".")[-1])
        combined_text += text + "\n"

    result = extract_legal_issues(combined_text, province_code=current_user.province)
    issues = result['issues']
    keywords = result['keywords_found']
    merit_score = score_merit(issues, province=current_user.province, matched_keywords=keywords)

    issue_category = next(iter(issues)) if issues else "Small Claims"
    user_fields = {
        "FULL_NAME": current_user.full_name,
        "ADDRESS": current_user.address,
        "PHONE": current_user.phone,
        "POSTAL_CODE": current_user.postal_code,
        "PROVINCE": current_user.province,
        "CASE_TITLE": case.title
    }

    docx_path, pdf_path = generate_legal_form(issue_category, current_user.province, user_fields, case.id)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        zip_file.write(docx_path, os.path.basename(docx_path))
        if pdf_path:
            zip_file.write(pdf_path, os.path.basename(pdf_path))
        for ev in case.evidence:
            zip_file.write(ev.file_path, os.path.basename(ev.file_path))
    zip_buffer.seek(0)

    flash(f"Merit Score: {merit_score:.2f}%", "info")
    return send_file(zip_buffer, mimetype='application/zip',
                     download_name=f"SmartDispute_Package_{case.title}.zip", as_attachment=True)

# --- PDF Preview ---
@routes.route("/generate-pdf-preview/<int:case_id>")
@login_required
def generate_pdf_preview(case_id):
    case = Case.query.get_or_404(case_id)
    if case.user_id != current_user.id:
        flash("Unauthorized", "danger")
        return redirect(url_for("routes.dashboard"))

    html = render_template("pdf_preview.html", case=case, user=current_user)
    pdf = HTML(string=html).write_pdf()

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=SmartDispute_Preview_{case.title}.pdf'

    return response

# --- Payment Page ---
@routes.route("/pay/<int:case_id>")
@login_required
def pay_for_case(case_id):
    case = Case.query.get_or_404(case_id)
    if case.user_id != current_user.id:
        flash("Unauthorized", "danger")
        return redirect(url_for("routes.dashboard"))

    paid = Payment.query.filter_by(case_id=case_id, status="completed").first()
    if paid or current_user.subscription_type == "unlimited":
        flash("Payment already completed for this case.", "info")
        return redirect(url_for("routes.generate_legal_package", case_id=case.id))

    return render_template("pay_etf.html", case=case)

# Register blueprint in __init__.py:
# app.register_blueprint(routes)
