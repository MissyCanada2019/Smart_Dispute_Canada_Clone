from flask import request, jsonify, render_template
from src.server.models import db, Case

def register_routes(app):
    # Homepage Route
    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")  # Make sure templates/index.html exists

    # CanLII Keyword Search (Mocked)
    @app.route("/canlii-search", methods=["POST"])
    def canlii_search():
        keyword = request.form.get("keyword")
        results = [{
            "title": f"Sample Case Related to {keyword}",
            "url": f"https://www.canlii.org/en/ca/search/?keyword={keyword}"
        }]
        return jsonify(results)

    # Save a Legal Case to DB
    @app.route("/save-case", methods=["POST"])
    def save_case():
        title = request.form["title"]
        url = request.form["url"]
        new_case = Case(title=title, url=url)
        db.session.add(new_case)
        db.session.commit()
        return "Saved"

    # Dashboard View
    @app.route("/dashboard", methods=["GET"])
    def dashboard():
        cases = Case.query.all()
        return render_template("dashboard.html", cases=cases)  # Ensure dashboard.html exists
