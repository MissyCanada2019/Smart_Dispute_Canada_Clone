import os
from flask import request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from src.server.models import db, User, Case, Evidence
from utils.ocr import extract_text_from_file
from utils.issue_classifier import classify_legal_issue
from utils.merit_weight import score_merit
from utils.form_selector import select_form
from utils.document_generator import generate_legal_form


def register_routes(app):
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]
            if User.query.filter_by(email=email).first():
                flash("Email already registered", "danger")
                return redirect(url_for("register"))
            hashed_pw = generate_password_hash(password)
            user = User(email=email, password=hashed_pw)
            db.session.add(user)
            db.session.commit()
            flash("Registration successful", "success")
            return redirect(url_for("login"))
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]
            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password, password):
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
        user_cases = Case.query.filter_by(user_id=current_user.id).all()
        return render_template("dashboard.html", cases=user_cases)

    @app.route("/create-case", methods=["GET", "POST"])
    @login_required
    def create_case():
        if request.method == "POST":
            title = request.form["title"]
            description = request.form["description"]
            new_case = Case(title=title, description=description, user_id=current_user.id)
            db.session.add(new_case)
            db.session.commit()
            flash("Case created successfully", "success")
            return redirect(url_for("upload"))
        return render_template("create_case.html")

    @app.route("/upload", methods=["GET", "POST"])
    @login_required
    def upload():
        cases = Case.query.filter_by(user_id=current_user.id).all()
        if request.method == "POST":
            case_id = request.form["case_id"]
            tag = request.form.get("tag")
            file = request.files.get("document")

            if file:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
                file.save(filepath)

                evidence = Evidence(
                    case_id=case_id,
                    user_id=current_user.id,
                    filename=filename,
                    file_path=filepath,
                    tag=tag
                )
                db.session.add(evidence)
                db.session.commit()

                # AI processing
                text, _ = extract_text_from_file(filepath)
                legal_topic, confidence = classify_legal_issue(text, current_user.province)
                evidence.tag = legal_topic
                db.session.commit()

                flash(f"File uploaded. AI classified this as: {legal_topic} ({confidence}% confidence).", "info")
                return redirect(url_for("review_case", case_id=case_id))
            else:
                flash("No file selected", "danger")

        return render_template("upload.html", cases=cases)

    @app.route("/review-case/<int:case_id>")
    @login_required
    def review_case(case_id):
        case = Case.query.get_or_404(case_id)
        evidence = Evidence.query.filter_by(case_id=case.id).first()
        issue_type = evidence.tag or "general"

        # Score the merit
        text, _ = extract_text_from_file(evidence.file_path)
        score_data = score_merit(text, issue_type, province=current_user.province)
        merit_score = score_data["merit_score"]
        explanation = "This score reflects how strong your evidence is compared to similar winning cases in Canada."

        # Get form info
        form_info = select_form(issue_type, current_user.province)

        return render_template("review_case.html", case=case, merit_score=merit_score,
                               explanation=explanation, form_info=form_info)

    @app.route("/confirm-payment/<int:case_id>", methods=["POST"])
    @login_required
    def confirm_payment(case_id):
        flash("Payment confirmation pending. You'll receive access shortly.", "info")
        return redirect(url_for("review_case", case_id=case_id))
