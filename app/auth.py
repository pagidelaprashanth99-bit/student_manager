from flask import Blueprint, render_template, request, redirect, flash
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import User
from app import db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        if not username or not password:
            flash("Please enter both username and password.", "error")
            return render_template("login.html")
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect("/teacher/dashboard" if user.role == "teacher" else "/student/dashboard")
        else:
            flash("Invalid username or password. Please try again.", "error")
            return render_template("login.html")
    
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect("/")
