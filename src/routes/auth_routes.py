from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user
from services.user_service import register_user
from src.models import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")

        try:
            user = register_user(email, password, first_name, last_name)
            flash("Registration successful. You can now log in.", "success")
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
            login_user(user)
            return redirect(url_for("main.dashboard"))
        else:
            flash("Invalid credentials.", "danger")

    return render_template("login.html")
