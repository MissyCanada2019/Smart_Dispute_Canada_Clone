import os
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from src.server.extensions import db, send_receipt
from src.models import Case, Evidence, Payment, User
from src.server.ai_helpers import extract_text_from_file, classify_legal_issue, score_merit, select_form
from src.server.payments import verify_paypal_payment
from src.steps_scraper import run_scraper
from src.server.canlii_scraper import search_canlii  # Optional

main = Blueprint("main", __name__)

UPLOAD_FOLDER = "uploads"
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
    cases = Case.query.filter_by(user_id=current_user.id).all()

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        tag = request.form.get("tag")
        file = request.files.get("document")

        if file:
            filename = secure_filename(file.filename)
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            file.save(save_path)

            # AI analysis
            text, _ = extract_text_from_file(save_path)
            legal_issue = classify_legal_issue(text)
            score = score_merit(text, legal_issue)
            keywords, form_info = select_form(legal_issue, current_user.province)

            # Scrape Steps to Justice content
            run_scraper()  # Optional: pass legal_issue for targeted scrape

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
                           merit_score=case.confidence_score,
                           form_info=form_info,
                           explanation="Your case shows strong legal grounds.")

@main.route("/confirm-payment/<int:case_id>", methods=["POST"])
@login_required
def confirm_payment(case_id):
    case = Case.query.get_or_404(case_id)
    if case.user_id != current_user.id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("main.dashboard"))

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

    flash("Payment confirmed! You can now download your legal package.", "success")
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

        flash("PayPal payment verified! Legal package unlocked.", "success")
    elif status == "mismatch":
        flash("Payment amount or currency mismatch.", "danger")
    elif status == "pending":
        flash("Payment still pending.", "warning")
    else:
        flash("Payment verification failed.", "danger")

    return redirect(url_for("main.review_case", case_id=case_id))

@main.route("/download/<int:case_id>")
@login_required
def download_legal_package(case_id):
    case = Case.query.get_or_404(case_id)
    if not case.is_paid:
        flash("Please complete payment before downloading.", "warning")
        return redirect(url_for("main.review_case", case_id=case.id))
    return send_file("static/sample_form.pdf", as_attachment=True)

@main.route("/admin")
@login_required
def admin_panel():
    if not current_user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for("main.dashboard"))
    users = User.query.all()
    return render_template("admin_dashboard.html", users=users)

@main.route("/admin/promote/<int:user_id>")
@login_required
def promote_user(user_id):
    if not current_user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for("main.dashboard"))
    user = User.query.get_or_404(user_id)
    user.subscription_type = "unlimited"
    user.subscription_end = datetime.utcnow() + timedelta(days=365)
    db.session.commit()
    flash(f"{user.full_name} promoted to unlimited access.", "success")
    return redirect(url_for("main.admin_panel"))

@main.route("/admin/revoke/<int:user_id>")
@login_required
def revoke_admin(user_id):
    if current_user.email != "teresa.bertin@smartdispute.com":
        flash("Only the owner can revoke admin access.", "danger")
        return redirect(url_for("main.dashboard"))
        user = User.query.get_or_404(user_id)
    user.is_admin = False
    db.session.commit()
    flash("Admin privileges revoked.", "warning")
    return redirect(url_for("main.admin_panel"))

@main.route("/canlii-search", methods=["GET", "POST"])
@login_required
def canlii_search():
    results = []
    searched = None

    if request.method == "POST":
        keyword = request.form.get("keyword")
        searched = keyword
        results = search_canlii(keyword, jurisdiction=current_user.province or "on")

    return render_template("search.html", results=results, searched=searched)

@main.route("/legal-help/<int:case_id>")
@login_required
def show_legal_help(case_id):
    case = Case.query.get_or_404(case_id)
    if case.user_id != current_user.id:
        flash("Access denied.", "danger")
        return redirect(url_for("main.dashboard"))

    from src.models import LegalReference
    references = LegalReference.query.filter_by(case_id=case.id).all()
    return render_template("legal_help.html", case=case, references=references)

# OPTIONAL: Future route for generating legal forms
# @main.route("/generate-form/<int:case_id>")
# @login_required
# def generate_form(case_id):
#     # Generate filled-out DOCX or PDF from FormTemplate based on legal_issue
#     pass
