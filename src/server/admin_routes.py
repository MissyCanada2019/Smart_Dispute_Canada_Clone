from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from src.models import db, User, Case, Evidence

def register_admin_routes(app):
    @app.route("/admin")
    @login_required
    def admin_dashboard():
        if not current_user.is_admin:
            flash("Access denied", "danger")
            return redirect(url_for("main.dashboard"))

        users = User.query.all()
        user_stats = []

        for user in users:
            user_stats.append({
                "id": user.id,
                "name": user.full_name,
                "email": user.email,
                "cases": len(user.cases),
                "evidence": len(user.evidence),
                "subscription": user.subscription_type,
                "admin": user.is_admin
            })

        return render_template("admin_dashboard.html", user_stats=user_stats)

    return app
