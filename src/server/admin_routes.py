from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from src.models import db, User
from datetime import datetime, timedelta
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()

def register_admin_routes(app):
    csrf.init_app(app)

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

    @app.route("/admin/promote/<int:user_id>", methods=["POST"])
    @login_required
    def promote_user(user_id):
        if not current_user.is_admin:
            flash("Unauthorized", "danger")
            return redirect(url_for("admin_dashboard"))

        user = User.query.get_or_404(user_id)
        user.is_admin = True
        db.session.commit()
        flash(f"{user.email} has been promoted to admin.", "success")
        return redirect(url_for("admin_dashboard"))

    @app.route("/admin/upgrade/<int:user_id>", methods=["POST"])
    @login_required
    def upgrade_user(user_id):
        if not current_user.is_admin:
            flash("Unauthorized", "danger")
            return redirect(url_for("admin_dashboard"))

        user = User.query.get_or_404(user_id)
        user.subscription_type = "unlimited"
        user.subscription_end = datetime.utcnow() + timedelta(days=365)
        db.session.commit()
        flash(f"{user.email} has been upgraded to Unlimited.", "success")
        return redirect(url_for("admin_dashboard"))

    return app
