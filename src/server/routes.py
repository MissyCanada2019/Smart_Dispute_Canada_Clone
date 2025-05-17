from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from src.models import db, Case, Evidence, Payment
from src.server.ai_helpers import extract_text_from_file, classify_legal_issue, score_merit, select_form
from src.server.payments import process_paypal_payment
import os
from io import BytesIO

main = Blueprint("main", __name__)

@main.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    cases = Case.query.filter_by(user_id=current_user.id).all()
    if request.method == "POST":
        case_title = request.form.get("case_title")
        case_category = request.form.get("case_category")
        files = request.files.getlist("files[]")

        new_case = Case(user_id=current_user.id, title=case_title, description=case_category)
        db.session.add(new_case)
        db.session.commit()

        saved_files = []
        for file in files:
            if file:
                filename = secure_filename(file.filename)
                user_folder = os.path.join(current_app.config["UPLOAD_FOLDER"], str(current_user.id), str(new_case.id))
                os.makedirs(user_folder, exist_ok=True)
                file_path = os.path.join(user_folder, filename)
                file.save(file_path)

                evidence = Evidence(
                    case_id=new_case.id,
                    user_id=current_user.id,
                    filename=filename,
                    file_path=file_path
                )
                db.session.add(evidence)
                saved_files.append(file_path)

        db.session.commit()

        combined_text = ""
        for path in saved_files:
            text, _ = extract_text_from_file(path)
            combined_text += f"\n{text}"

        legal_issue = classify_legal_issue(combined_text)
        matched_keywords = ", ".join(legal_issue.get("keywords", []))
        confidence_score = legal_issue.get("confidence", 0)
        form_info = select_form(legal_issue.get("issue", ""), current_user.province)

        new_case.legal_issue = legal_issue.get("issue")
        new_case.matched_keywords = matched_keywords
        new_case.confidence_score = confidence_score
        db.session.commit()

        flash("Case uploaded and analyzed. Review results below.", "success")
        return redirect(url_for("main.review_case", case_id=new_case.id))

    return render_template("upload.html", cases=cases)

@main.route("/review/<int:case_id>")
@login_required
def review_case(case_id):
    case = Case.query.get_or_404(case_id)
    if case.user_id != current_user.id:
        flash("Unauthorized access", "danger")
        return redirect(url_for("dashboard"))

    form_info = select_form(case.legal_issue, current_user.province)
    explanation = "This form was selected based on the legal issue and keywords identified in your uploaded evidence."
    return render_template("review_case.html", case=case, form_info=form_info, merit_score=case.confidence_score, explanation=explanation)

@main.route("/confirm_payment/<int:case_id>", methods=["POST"])
@login_required
def confirm_payment(case_id):
    case = Case.query.get_or_404(case_id)
    if case.user_id != current_user.id:
        flash("Unauthorized action", "danger")
        return redirect(url_for("dashboard"))

    payment_id = request.form.get("paypal_payment_id")
    if payment_id:
        status = process_paypal_payment(payment_id, expected_amount=9.99)
        if status != "completed":
            flash("PayPal payment failed or not verified", "danger")
            return redirect(url_for("main.review_case", case_id=case_id))
        payment_method = "paypal"
    else:
        payment_method = "e-transfer"

    case.is_paid = True
    payment = Payment(
        case_id=case.id,
        user_id=current_user.id,
        amount=9.99,
        payment_type="legal_package",
        payment_method=payment_method,
        payment_id=payment_id,
        status="completed"
    )
    db.session.add(payment)
    db.session.commit()

    flash("Payment confirmed. You can now download your legal package.", "success")
    return redirect(url_for("main.review_case", case_id=case_id))

@main.route("/download/<int:case_id>")
@login_required
def download_legal_package(case_id):
    case = Case.query.get_or_404(case_id)
    if case.user_id != current_user.id or not case.is_paid:
        flash("Access denied or unpaid case.", "danger")
        return redirect(url_for("dashboard"))

    dummy_file = BytesIO()
    dummy_file.write(b"This is your SmartDispute legal package.")
    dummy_file.seek(0)

    return send_file(dummy_file, as_attachment=True, download_name="SmartDispute_Package.docx", mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
