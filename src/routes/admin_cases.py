# src/routes/admin_cases.py

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from src.models import User, Case
from src.server.extensions import db

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash("Access denied", "danger")
        return redirect(url_for("main.dashboard"))

    users = User.query.all()
    user_stats = []

    for user in users:
        stats = {
            "id": user.id,
            "name": user.full_name,
            "email": user.email,
            "subscription": user.subscription_plan or "free",
            "cases": len(user.cases),
            "evidence": sum(len(c.evidence_files) for c in user.cases),
            "admin": user.is_admin
        }
        user_stats.append(stats)

    return render_template("admin_dashboard.html", user_stats=user_stats)


@admin_bp.route("/promote/<int:user_id>", methods=["POST"])
@login_required
def promote_user(user_id):
    if not current_user.is_admin:
        flash("Access denied", "danger")
        return redirect(url_for("main.dashboard"))

    user = User.query.get_or_404(user_id)
    user.is_admin = True
    db.session.commit()
    flash(f"{user.full_name} has been promoted to admin.", "success")
    return redirect(url_for("admin.admin_dashboard"))


@admin_bp.route("/revoke/<int:user_id>", methods=["POST"])
@login_required
def revoke_admin(user_id):
    if not current_user.is_admin:
        flash("Access denied", "danger")
        return redirect(url_for("main.dashboard"))

    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot revoke your own admin status.", "warning")
        return redirect(url_for("admin.admin_dashboard"))

    user.is_admin = False
    db.session.commit()
    flash(f"Admin rights revoked from {user.full_name}.", "info")
    return redirect(url_for("admin.admin_dashboard"))


@admin_bp.route("/upgrade/<int:user_id>", methods=["POST"])
@login_required
def upgrade_user(user_id):
    if not current_user.is_admin:
        flash("Access denied", "danger")
        return redirect(url_for("main.dashboard"))

    user = User.query.get_or_404(user_id)
    user.subscription_plan = "unlimited"
    db.session.commit()
    flash(f"{user.full_name}'s plan upgraded to Unlimited.", "success")
    return redirect(url_for("admin.admin_dashboard"))
