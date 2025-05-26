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
