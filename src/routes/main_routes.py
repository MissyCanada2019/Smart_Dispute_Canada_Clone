import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user

from src.models import Case
from src.server.case_service import handle_upload, prepare_review_data
from src.server.services.payment_service import confirm_e_transfer, confirm_paypal_payment
from src.server.services.doc_service import get_preview_path, get_download_path

main = Blueprint("main", __name__)

# Homepage route
@main.route("/")
def home():
    print("Looking for index.html at:", os.path.abspath("src/templates/index.html"))
    return render_template("index.html")

# About page route
@main.route("/about")
def about():
    return render_template("about.html")

# Dashboard view (requires login)
@main.route("/dashboard")
@login_required
def dashboard():
    cases = Case.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", cases=cases)

# Upload evidence/documents
@main.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        return handle_upload(request, current_user)
    cases = Case.query.filter_by(user_id=current_user.id).all()
    return render_template("upload.html", cases=cases)

# Review case details + merit score
@main.route("/review/<int:case_id>")
@login_required
def review_case(case_id):
    case, form_info, merit_score, explanation, email = prepare_review_data(case_id, current_user)
    if not case:
        flash("Access denied.", "danger")
        return redirect(url_for("main.dashboard"))

    return render_template(
        "review_case.html",
        case=case,
        form_info=form_info,
        merit_score=merit_score,
        explanation=explanation,
        ETRANSFER_EMAIL=email
    )

# Preview generated document (not downloaded)
@main.route("/preview/<int:case_id>")
@login_required
def preview_case(case_id):
    path = get_preview_path(case_id, current_user)
    return send_file(path, as_attachment=False)

# Download legal document package
@main.route("/download/<int:case_id>")
@login_required
def download_legal_package(case_id):
    path = get_download_path(case_id, current_user)
    if not path:
        flash("Complete payment or subscribe to download.", "warning")
        return redirect(url_for("main.review_case", case_id=case_id))
    return send_file(path, as_attachment=True)

# Confirm e-transfer route
@main.route("/confirm-payment/<int:case_id>", methods=["POST"])
@login_required
def confirm_payment(case_id):
    return confirm_e_transfer(case_id, current_user)

# Confirm PayPal payment
@main.route("/paypal-confirm/<int:case_id>", methods=["POST"])
@login_required
def paypal_confirm(case_id):
    return confirm_paypal_payment(request, case_id, current_user)
