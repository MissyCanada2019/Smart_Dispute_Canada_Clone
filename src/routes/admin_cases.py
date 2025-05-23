<# src/routes/admin_cases.py

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from src.models import User, Case
from src.server.extensions import db

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin")
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for("main.dashboard"))

    cases = Case.query.all()
    users = User.query.all()
    return render_template("admin_dashboard.html", cases=cases, users=users)
