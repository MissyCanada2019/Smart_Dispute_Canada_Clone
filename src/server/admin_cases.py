from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from src.models import User, db

admin_bp = Blueprint("admin_bp", __name__)

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Access denied.", "danger")
            return redirect(url_for("main.dashboard"))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route("/admin/dashboard")
@login_required
@admin_required
def admin_dashboard():
    search = request.args.get("search", "").strip().lower()
    subscription = request.args.get("subscription", "").strip()

    query = User.query
    if search:
        query = query.filter(
            (User.full_name.ilike(f"%{search}%")) | 
            (User.email.ilike(f"%{search}%"))
        )
    if subscription:
        query = query.filter_by(subscription_type=subscription)

    users = query.all()
    user_stats = [{
        "id": u.id,
        "name": u.full_name,
        "email": u.email,
        "subscription": u.subscription_type,
        "cases": len(u.cases),
        "evidence": len(u.evidence),
        "admin": u.is_admin
    } for u in users]

    return render_template("admin_dashboard.html", user_stats=user_stats)

@admin_bp.route("/admin/promote/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def promote_user(user_id):
    if current_user.email != "teresa.bertin@smartdispute.com":
        flash("Only the owner can grant admin privileges.", "danger")
        return redirect(url_for("admin_bp.admin_dashboard"))

    user = User.query.get_or_404(user_id)
    user.is_admin = True
    db.session.commit()
    flash(f"{user.email} promoted to admin.", "success")
    return redirect(url_for("admin_bp.admin_dashboard"))

@admin_bp.route("/admin/revoke/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def revoke_admin(user_id):
    if current_user.email != "teresa.bertin@smartdispute.com":
        flash("Only the owner can revoke admin privileges.", "danger")
        return redirect(url_for("admin_bp.admin_dashboard"))

    user = User.query.get_or_404(user_id)
    user.is_admin = False
    db.session.commit()
    flash(f"{user.email} admin access revoked.", "warning")
    return redirect(url_for("admin_bp.admin_dashboard"))

@admin_bp.route("/admin/upgrade/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def upgrade_user(user_id):
    user = User.query.get_or_404(user_id)
    user.subscription_type = "unlimited"
    from datetime import datetime, timedelta
    user.subscription_end = datetime.utcnow() + timedelta(days=365)
    db.session.commit()
    flash(f"{user.email} upgraded to unlimited access.", "success")
    return redirect(url_for("admin_bp.admin_dashboard"))
