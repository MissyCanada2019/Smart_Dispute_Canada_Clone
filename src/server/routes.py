from flask import request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from src.server.models import db, User, Case, Evidence
import os
from datetime import datetime

def register_routes(app):
    # Home
    @app.route("/")
    def index():
        return render_template("index.html")

    # Register
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

    # Login
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

    # Logout
    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("Logged out", "info")
        return redirect(url_for("login"))

    # Dashboard
    @app.route("/dashboard")
    @login_required
    def dashboard():
        user_cases = Case.query.filter_by(user_id=current_user.id).all()
        return render_template("dashboard.html", cases=user_cases)

    # Create a Case
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

    # Upload Evidence
    @app.route("/upload", methods=["GET", "POST"])
    @login_required
    def upload():
        cases = Case.query.filter_by(user_id=current_user.id).all()
        if request.method == "POST":
            case_id = request.form["case_id"]
            tag = request.form.get("tag")
            notes = request.form.get("notes")
            file = request.files.get("document")

            if file:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
                file.save(filepath)

                # Create Evidence entry
                evidence = Evidence(
                    case_id=case_id,
                    user_id=current_user.id,
                    filename=filename,
                    file_path=filepath,
                    tag=tag
                )
                db.session.add(evidence)
                db.session.commit()

                # Trigger AI scan (this is where your merit logic will go)
                flash("File uploaded. AI scan and legal analysis starting...", "info")

                # You can now run your AI tagging/merit function like:
                # trigger_ai_merit_analysis(filepath, evidence_id=evidence.id)

                return redirect(url_for("dashboard"))
            else:
                flash("No file selected", "danger")

        return render_template("upload.html", cases=cases)
