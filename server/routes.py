from flask import request, redirect, render_template, url_for, flash
from flask_login import login_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

from server import app, db
from server.models import User, GeneratedForm
from utils.ocr import process_document
from utils.document_generator import generate_legal_form

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email already registered", "danger")
            return redirect(url_for("register"))

        new_user = User(
            email=email,
            password_hash=generate_password_hash(password),
            full_name=request.form["full_name"],
            address=request.form["address"],
            phone=request.form["phone"],
            postal_code=request.form["postal_code"],
            province=request.form["province"],
            date_of_birth=request.form["date_of_birth"]
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("dashboard"))

    return render_template("register.html")


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        uploaded_file = request.files["document"]
        if uploaded_file:
            filename = secure_filename(uploaded_file.filename)
            upload_path = os.path.join("uploads", filename)
            uploaded_file.save(upload_path)

            text, metadata = process_document(upload_path, filename.split(".")[-1])

            # Auto-fill form using user data
            form_data = {
                "FULL_NAME": current_user.full_name or "",
                "ADDRESS": current_user.address or "",
                "PHONE": current_user.phone or "",
                "POSTAL_CODE": current_user.postal_code or "",
                "PROVINCE": current_user.province or "",
                "DATE_OF_BIRTH": current_user.date_of_birth or ""
            }

            template_path = "templates/forms/sample_template.docx"
            output_path = f"generated_forms/{current_user.id}_{filename}.docx"
            generate_legal_form(template_path, output_path, form_data)

            new_form = GeneratedForm(
                user_id=current_user.id,
                form_name="Auto-Generated Form",
                file_path=output_path
            )
            db.session.add(new_form)
            db.session.commit()

            flash("Your document was processed and form generated.", "success")
            return redirect(url_for("dashboard"))

    return render_template("upload.html")

from flask import request, redirect, render_template, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash

from server.models import User
from server import app, db

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))
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
