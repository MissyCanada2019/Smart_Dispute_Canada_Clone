import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from src.server.extensions import db, send_receipt
from src.models import Case, Evidence, Payment, User
from src.server.ai_helpers import extract_text_from_file, classify_legal_issue, score_merit, select_form
from src.server.payments import verify_paypal_payment
from src.server.document_generator import generate_docx, generate_watermarked_preview
from src.steps_scraper import run_scraper

main = Blueprint("main", __name__)
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
ETRANSFER_EMAIL = "smartdisputecanada@gmail.com"


@main.route("/")
def home():
    return render_template("index.html")


@main.route("/dashboard")
@login_required
def dashboard():
    cases = Case.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", cases=cases)


@main.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        tag = request.form.get("tag")
        file = request.files.get("document")

        if file:
            filename = secure_filename(file.filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(save_path)

            # AI-assisted analysis
            text, _ = extract_text_from_file(save_path)
            legal_issue = classify_legal_issue(text)
            score = score_merit(text, legal_issue)
            keywords, form_info = select_form(legal_issue, current_user.province)

            run_scraper()

            # Save case
            new_case = Case(
                user_id=current_user.id,
                title=title,
                description=description,
                legal_issue=legal_issue,
                confidence_score=score,
                matched_keywords=keywords,
                is_paid=False
            )
            db.session.add(new_case)
            db.session.commit()

            # Save evidence
            evidence = Evidence(
                user_id=current_user.id,
                case_id=new_case.id,
                filename=filename,
                file_path=save_path,
                tag=tag
            )
            db.session.add(evidence)
            db.session.commit()

            return redirect(url_for("main.review_case", case_id=new_case.id))

    cases = Case.query.filter_by(user_id=current_user.id).all()
    return render_template("upload.html", cases=cases)


@main.route("/review/<int:case_id>")
@login_required
def review_case(case_id):
    case = Case.query.get_or_404(case_id)
    if case.user_id != current_user.id:
        flash("Access denied.", "danger")
        return redirect(url_for("main.dashboard"))

    form_info = select_form(case.legal_issue, current_user.province)[1]
    return render_template("review_case.html", case=case,
                           form_info=form_info,
                           merit_score=case.confidence_score,
                           explanation="Your case shows strong legal grounds.",
                           ETRANSFER_EMAIL=ETRANSFER_EMAIL)


@main.route("/preview/<int:case_id>")
@login_required
def preview_case(case_id):
    case = Case.query.get_or_404(case_id)
    if case.user_id != current_user.id:
        return "Unauthorized", 403

    if case.is_paid or current_user.subscription_type in ["monthly", "yearly"]:
        doc_path = generate_docx(case.id)
    else:
        doc_path = generate_watermarked_preview(case.id)

    return send_file(doc_path, as_attachment=False)


@main.route("/download/<int:case_id>")
@login_required
def download_legal_package(case_id):
    case = Case.query.get_or_404(case_id)
    if not case.is_paid and current_user.subscription_type not in ["monthly", "yearly"]:
        flash("Complete payment or subscribe to download.", "warning")
        return redirect(url_for("main.review_case", case_id=case.id))

    doc_path = generate_docx(case.id)
    return send_file(doc_path, as_attachment=True)


@main.route("/confirm-payment/<int:case_id>", methods=["POST"])
@login_required
def confirm_payment(case_id):
    case = Case.query.get_or_404(case_id)
    if case.user_id != current_user.id:
        return "Unauthorized", 403

    case.is_paid = True
    db.session.commit()

    payment = Payment(
        case_id=case.id,
        user_id=current_user.id,
        amount=9.99,
        payment_type="legal_package",
        payment_method="e-transfer",
        status="completed",
        created_at=datetime.utcnow()
    )
    db.session.add(payment)
    db.session.commit()

    send_receipt(current_user.email, case.title, "e-transfer")
    flash("Payment confirmed. Document unlocked.", "success")
    return redirect(url_for("main.review_case", case_id=case.id))


@main.route("/paypal-confirm/<int:case_id>", methods=["POST"])
@login_required
def paypal_confirm(case_id):
    payment_id = request.form.get("payment_id")
    expected_amount = 9.99
    status = verify_paypal_payment(payment_id, expected_amount)

    if status == "completed":
        case = Case.query.get_or_404(case_id)
        case.is_paid = True
        db.session.commit()

        payment = Payment(
            case_id=case.id,
            user_id=current_user.id,
            amount=expected_amount,
            payment_type="legal_package",
            payment_method="paypal",
            status="completed",
            created_at=datetime.utcnow()
        )
        db.session.add(payment)
        db.session.commit()

        send_receipt(current_user.email, case.title, "PayPal")
        flash("PayPal payment verified. Document unlocked.", "success")
    else:
        flash("Payment failed or pending.", "danger")

    return redirect(url_for("main.review_case", case_id=case_id))
