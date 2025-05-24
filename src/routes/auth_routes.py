# src/routes/auth_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash

from src.models import db, User
from src.server.forms import LoginForm, RegistrationForm

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("main.dashboard"))
        else:
            flash("Invalid email or password.", "danger")
    return render_template("login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data.lower()).first()
        if existing_user:
            flash("An account with this email already exists.", "warning")
            return redirect(url_for("auth.register"))

        new_user = User(
            email=form.email.data.lower(),
            password_hash=generate_password_hash(form.password.data),
            full_name=form.full_name.data,
            address=form.address.data,
            phone=form.phone.data,
            postal_code=form.postal_code.data,
            province=form.province.data
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash("Registration successful! Welcome.", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("register.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You’ve been logged out.", "info")
    return redirect(url_for("auth.login"))
