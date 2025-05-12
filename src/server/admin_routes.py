from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from src.server.models import db, Case

def register_admin_routes(app):
    @app.route("/admin/cases")
    @login_required
    def admin_cases():
        if not current_user.is_admin:
            flash("Access denied", "danger")
            return redirect(url_for("dashboard"))

        unpaid_cases = Case.query.filter_by(is_paid=False).all()
        return render_template("admin_cases.html", cases=unpaid_cases)

    @app.route("/admin/unlock/<int:case_id>", methods=["POST"])
    @login_required
    def admin_unlock_case(case_id):
        if not current_user.is_admin:
            flash("Unauthorized", "danger")
            return redirect(url_for("dashboard"))

        case = Case.query.get_or_404(case_id)
        case.is_paid = True
        db.session.commit()
        flash(f"Case {case.id} marked as paid and unlocked.", "success")
        return redirect(url_for("admin_cases"))
