import os
from flask import request, render_template, redirect, url_for, flash, send_file
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from src.server.models import db, User, Case, Evidence
from utils.ocr import extract_text_from_file
from utils.issue_classifier import classify_legal_issue
from utils.merit_weight import score_merit
from utils.form_selector import select_form
from utils.document_generator import generate_legal_form
from utils.email_utils import send_email

def register_routes(app):
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route("/pricing")
    def pricing():
        return render_template("pricing.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]
            if User.query.filter_by(email=email).first():
                flash("Email already registered", "danger")
                return redirect(url_for("register"))
            user = User(email=email, password_hash=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            flash("Registered successfully!", "success")
            return redirect(url_for("login"))
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]
            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                return redirect(url_for("dashboard"))
            flash("Invalid credentials", "danger")
        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("Logged out", "info")
        return redirect(url_for("login"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        cases = Case.query.filter_by(user_id=current_user.id).all()
        return render_template("dashboard.html", cases=cases)

    @app.route("/create-case", methods=["GET", "POST"])
    @login_required
    def create_case():
        if request.method == "POST":
            title = request.form["title"]
            description = request.form["description"]
            new_case = Case(title=title, description=description, user_id=current_user.id)
            db.session.add(new_case)
            db.session.commit()
            flash("Case created successfully.", "success")
            return redirect(url_for("upload"))
        return render_template("create_case.html")

    @app.route("/upload", methods=["GET", "POST"])
    @login_required
    def upload():
        user_cases = Case.query.filter_by(user_id=current_user.id).all()
        if request.method == "POST":
            case_id = request.form["case_id"]
            tag = request.form.get("tag")
            file = request.files.get("document")

            if file:
                filename = secure_filename(file.filename)
                save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
                file.save(save_path)

                new_evidence = Evidence(
                    case_id=case_id,
                    user_id=current_user.id,
                    filename=filename,
                    file_path=save_path,
                    tag=tag
                )
                db.session.add(new_evidence)
                db.session.commit()

                text, _ = extract_text_from_file(save_path)
                legal_tag, confidence = classify_legal_issue(text, current_user.province)
                new_evidence.tag = legal_tag
                db.session.commit()

                flash(f"Evidence uploaded. AI classified issue as '{legal_tag}' ({confidence}%).", "info")
                return redirect(url_for("review_case", case_id=case_id))
            else:
                flash("No file selected", "danger")

        return render_template("upload.html", cases=user_cases)

    @app.route("/review-case/<int:case_id>")
    @login_required
    def review_case(case_id):
        case = Case.query.get_or_404(case_id)
        evidence = Evidence.query.filter_by(case_id=case.id).first()
        issue_type = evidence.tag or "general"
        text, _ = extract_text_from_file(evidence.file_path)

        score_data = score_merit(text, issue_type, current_user.province)
        merit_score = score_data["merit_score"]
        explanation = "This score reflects how strong your evidence is compared to similar winning cases in Canada."

        form_info = select_form(issue_type, current_user.province)

        return render_template("review_case.html", case=case, merit_score=merit_score,
                               explanation=explanation, form_info=form_info)

    @app.route("/confirm-payment/<int:case_id>", methods=["POST"])
    @login_required
    def confirm_payment(case_id):
        case = Case.query.get_or_404(case_id)
        send_email(
            subject="SmartDispute Payment Received",
            recipient="smartdisputecanada@gmail.com",
            body=f"Payment received for Case ID {case.id} from user {current_user.email}.\nUnlock form if confirmed."
        )
        flash("Payment confirmation sent. We'll unlock your form once verified.", "info")
        return redirect(url_for("review_case", case_id=case_id))

    @app.route("/admin/cases")
    @login_required
    def admin_cases():
        if not current_user.is_admin:
            flash("Access denied", "danger")
            return redirect(url_for("dashboard"))
        unpaid_cases = Case.query.filter_by(is_paid=False).all()
        return render_template("admin_cases.html", cases=unpaid_cases)

    @app.route("/admin/unlock/<int:case_id>", methods=["POST"])
    @login_required
    def admin_unlock_case(case_id):
        if not current_user.is_admin:
            flash("Unauthorized", "danger")
            return redirect(url_for("dashboard"))

        case = Case.query.get_or_404(case_id)
        case.is_paid = True
        db.session.commit()
        flash(f"Case {case.id} unlocked for download.", "success")
        return redirect(url_for("admin_cases"))

    @app.route("/download-form/<int:case_id>")
    @login_required
    def download_form(case_id):
        case = Case.query.get_or_404(case_id)
        if not case.is_paid:
            flash("Payment required to download this form.", "warning")
            return redirect(url_for("review_case", case_id=case_id))

        evidence = Evidence.query.filter_by(case_id=case.id).first()
        text, _ = extract_text_from_file(evidence.file_path)
        issue_type = evidence.tag or "general"

        form_info = select_form(issue_type, current_user.province)
        user_data = {
            "full_name": current_user.full_name or current_user.email,
            "address": current_user.address or "N/A",
            "phone": current_user.phone or "N/A",
            "province": current_user.province or "ON"
        }
        case_data = {
            "id": case.id,
            "title": case.title,
            "description": case.description or "",
            "tag": evidence.tag or ""
        }

        docx_path, _ = generate_legal_form(form_info, user_data, case_data)
        return send_file(docx_path, as_attachment=True)
