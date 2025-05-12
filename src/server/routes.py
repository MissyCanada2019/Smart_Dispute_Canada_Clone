from flask import request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from src.server.models import db, User, UploadedFile
import os

def register_routes(app):

    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash("Email already registered", "danger")
                return redirect(url_for("register"))
            hashed_pw = generate_password_hash(password)
            user = User(email=email, password=hashed_pw)
            db.session.add(user)
            db.session.commit()
            flash("Registered successfully!", "success")
            return redirect(url_for("login"))
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")
            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                flash("Login successful!", "success")
                return redirect(url_for("dashboard"))
            else:
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
        files = UploadedFile.query.filter_by(user_id=current_user.id).all()
        return render_template("dashboard.html", files=files)

    @app.route("/upload", methods=["GET", "POST"])
    @login_required
    def upload():
        if request.method == "POST":
            file = request.files.get("file")
            case_type = request.form.get("case_type")
            notes = request.form.get("notes")

            if file:
                filename = secure_filename(file.filename)
                save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(save_path)

                upload = UploadedFile(filename=filename, user_id=current_user.id, case_type=case_type, notes=notes)
                db.session.add(upload)
                db.session.commit()
                flash("File uploaded and saved!", "success")
            else:
                flash("No file selected", "danger")
        return render_template("upload.html")
