from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_login import login_user
from src.services.user_services import register_user
from src.models import User, db  # make sure db is imported

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        full_name = request.form.get("full_name")

        try:
            user = register_user(email, password, full_name)
            flash("Registration successful! Please check your email to confirm your account.", "success")
            return redirect(url_for("auth.login"))
        except ValueError as e:
            flash(str(e), "danger")

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if not user.is_verified:
                flash("Please confirm your email before logging in.", "warning")
                return redirect(url_for("auth.login"))

            login_user(user)
            return redirect(url_for("main.dashboard"))
        else:
            flash("Invalid credentials.", "danger")

    return render_template("login.html")


@auth_bp.route("/confirm/<token>")
def confirm_email(token):
    email = User.verify_confirmation_token(token)

    if not email:
        flash("Confirmation link is invalid or has expired.", "danger")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(email=email).first_or_404()

    if user.is_verified:
        flash("Account already verified. Please log in.", "info")
    else:
        user.is_verified = True
        db.session.commit()
        flash("Email confirmed! You can now log in.", "success")

    return redirect(url_for("auth.login"))
from flask_login import logout_user, login_required

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You've been logged out.", "info")
    return redirect(url_for("auth.login"))
