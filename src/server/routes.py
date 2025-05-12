from flask import request, jsonify, render_template, redirect, url_for, flash
from src.server.models import db, Case

def register_routes(app):
    # Homepage
    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")

    # Dashboard
    @app.route("/dashboard", methods=["GET"])
    def dashboard():
        cases = Case.query.all()
        return render_template("dashboard.html", cases=cases)

    # CanLII search (example mock)
    @app.route("/canlii-search", methods=["POST"])
    def canlii_search():
        keyword = request.form.get("keyword")
        results = [{
            "title": f"Sample Case Related to {keyword}",
            "url": f"https://www.canlii.org/en/ca/search/?keyword={keyword}"
        }]
        return jsonify(results)

    # Save a case
    @app.route("/save-case", methods=["POST"])
    def save_case():
        title = request.form["title"]
        url = request.form["url"]
        new_case = Case(title=title, url=url)
        db.session.add(new_case)
        db.session.commit()
        return "Saved"

    # Upload
    @app.route("/upload", methods=["GET", "POST"])
    def upload():
        if request.method == "POST":
            file = request.files.get("file")
            if file:
                flash("File uploaded successfully!", "success")
            else:
                flash("No file selected", "danger")
        return render_template("upload.html")

    # Login
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")
            flash("Login attempted", "info")
        return render_template("login.html")

    # Register
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")
            flash("Registration attempted", "info")
        return render_template("register.html")
