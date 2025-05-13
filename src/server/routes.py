import os
from flask import request, render_template, redirect, url_for, flash, send_file
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from src.models import db, User, Case, Evidence
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
            full_name = request.form.get("full_name")
            address = request.form.get("address")
            phone = request.form.get("phone")
            postal_code = request.form.get("postal_code")
            province = request.form.get("province")
            subscription_type = request.args.get("plan", "free")

            if User.query.filter_by(email=email).first():
                flash("Email already registered.", "danger")
                return redirect(url_for("register"))

            # Optional file upload (for low-income verification)
            if subscription_type == "low_income" and "verification_doc" in request.files:
                file = request.files["verification_doc"]
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    folder = os.path.join(app.config["UPLOAD_FOLDER"], "verification_docs")
                    os.makedirs(folder, exist_ok=True)
                    file.save(os.path.join(folder, filename))

            user = User(
                email=email,
                password_hash=generate_password_hash(password),
                full_name=full_name,
                address=address,
                phone=phone,
                postal_code=postal_code,
                province=province,
                subscription_type=subscription_type
            )
            db.session.add(user)
            db.session.commit()
            flash("Account created! Please login.", "success")
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
            case = Case(title=title, description=description, user_id=current_user.id)
            db.session.add(case)
            db.session.commit()
            flash("Case created successfully.", "success")
            return redirect(url_for("upload"))
        return render_template("create_case.html")

    @app.route("/upload", methods=["GET", "POST"])
    @login_required
    def upload():
        cases = Case.query.filter_by(user_id=current_user.id).all()
        if request.method == "POST":
            case_id = request.form["case_id"]
            file = request.files.get("document")
            if file:
                filename = secure_filename(file.filename)
                save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
                file.save(save_path)

                evidence = Evidence(case_id=case_id, user_id=current_user.id,
                                    filename=filename, file_path=save_path)
                db.session.add(evidence)
                db.session.commit()

                # AI analysis
                text, _ = extract_text_from_file(save_path)
                legal_issue = classify_legal_issue(text)
                merit_score = score_merit(text, legal_issue)
                form = select_form(legal_issue, current_user.province)

                flash(f"Evidence uploaded. Case scored {merit_score}% merit. Suggested form: {form}", "info")
                return redirect(url_for("review_case", case_id=case_id))
        return render_template("upload.html", cases=cases)

    @app.route("/review/<int:case_id>")
    @login_required
    def review_case(case_id):
        case = Case.query.get_or_404(case_id)
        return render_template("review_case.html", case=case)

    @app.route("/pay-etf/<int:case_id>")
    @login_required
    def pay_etf(case_id):
        case = Case.query.get_or_404(case_id)
        return render_template("pay_etf.html", case=case)
