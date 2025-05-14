from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from src.models import db, User, Case, Evidence

def register_admin_routes(app):
    @app.route("/admin")
    @login_required
    def admin_dashboard():
        if not current_user.is_admin:
            flash("Access denied", "danger")
            return redirect(url_for("dashboard"))
        users = User.query.all()
        return render_template("admin_dashboard.html", users=users)

    return app
