import os
import io
import zipfile
from flask import render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from server import db
from server.models import Case, Evidence, Payment
from utils.ocr import process_document
from utils.issue_classifier import extract_legal_issues
from utils.merit_weight import score_merit
from utils.document_generator import generate_legal_form


# --- Case Creation ---
@app.route("/create-case", methods=["GET", "POST"])
@login_required
def create_case():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form.get("description")
        new_case = Case(user_id=current_user.id, title=title, description=description)
        db.session.add(new_case)
        db.session.commit()
        flash("Case created successfully!", "success")
        return redirect(url_for("dashboard"))
    return render_template("create_case.html")


# --- Evidence Upload ---
@app.route("/upload", methods=["GET", "POST"])
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
            return redirect(url_for("dashboard"))
    return render_template("upload.html", cases=cases)


# --- Generate Legal Package with Merit Analysis ---
@app.route("/generate-legal-package/<int:case_id>")
@login_required
def generate_legal_package(case_id):
    case = Case.query.get_or_404(case_id)
    if case.user_id != current_user.id:
        flash("Unauthorized", "danger")
        return redirect(url_for("dashboard"))

    # Check for completed payment unless subscription is unlimited
    paid = Payment.query.filter_by(case_id=case_id, status="completed").first()
    if not paid and current_user.subscription_type != "unlimited":
        return redirect(url_for("pay_for_case", case_id=case.id))

    # Extract evidence text
    combined_text = ""
    for ev in case.evidence:
        text, _ = process_document(ev.file_path, ev.filename.split(".")[-1])
        combined_text += text + "\n"

    issues = extract_legal_issues(combined_text)
    merit_score = score_merit(issues, province=current_user.province)

    # Generate legal form
    form_path = f"generated_forms/case_{case.id}_form.docx"
    generate_legal_form("templates/forms/base_form.docx", form_path, {
        "FULL_NAME": current_user.full_name or "",
        "ADDRESS": current_user.address or "",
        "PHONE": current_user.phone or "",
        "POSTAL_CODE": current_user.postal_code or "",
        "PROVINCE": current_user.province or "",
        "CASE_TITLE": case.title
    })

    # Create ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        zip_file.write(form_path, os.path.basename(form_path))
        for ev in case.evidence:
            zip_file.write(ev.file_path, os.path.basename(ev.file_path))
    zip_buffer.seek(0)

    flash(f"Your case merit score: {merit_score:.2f}%", "info")
    return send_file(zip_buffer, mimetype='application/zip',
                     download_name=f"SmartDispute_Package_{case.title}.zip", as_attachment=True)


# --- Payment Page (E-Transfer Instructions) ---
@app.route("/pay/<int:case_id>")
@login_required
def pay_for_case(case_id):
    case = Case.query.get_or_404(case_id)
    if case.user_id != current_user.id:
        flash("Unauthorized", "danger")
        return redirect(url_for("dashboard"))

    # Payment already done
    paid = Payment.query.filter_by(case_id=case_id, status="completed").first()
    if paid or current_user.subscription_type == "unlimited":
        flash("Payment already completed for this case.", "info")
        return redirect(url_for("generate_legal_package", case_id=case.id))

    return render_template("pay_etf.html", case=case)
