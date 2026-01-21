import re
from flask import Blueprint, render_template, request, redirect, session, url_for, flash, session
from database import get_db_connection
from utils.validator import validate_email, validate_password
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
auth = Blueprint("auth", __name__)


@auth.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form["name"]
        email = request.form["email"]
        skills = request.form["skills"]
        raw_password = request.form["password"]
        confirm_password = request.form["confirm-password"]
        role = request.form["role"]

        #Validations
        is_valid_email, email = validate_email(email)
        if not is_valid_email:
            flash(email, "error")
            return redirect(url_for("auth.register"))

        is_valid_password, raw_password = validate_password(raw_password)
        if not is_valid_password:
            flash(raw_password, "error")
            return redirect(url_for("auth.register"))

         # Check if passwords match

        if raw_password != confirm_password:
            flash("Password do not match.", "error")
            return redirect(url_for("auth.register"))

        password_hash = generate_password_hash(raw_password)

        connection = get_db_connection()
        cursor = connection.cursor()


        sql = """
            INSERT INTO users (full_name, email, password_hash, skills, role)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (full_name, email, password_hash, skills, role))
        connection.commit()


        cursor.close()
        connection.close()

        flash("Account created successfully!", "success")
        return redirect(url_for("auth.login"))
    
    return render_template("register.html")
        
@auth.route("/login", methods = ["GET", "POST"])
    
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password!", "error")
            return redirect(url_for("auth.login"))
        if user["status"] != "active":
            flash("Your account is suspended contact support.", "error")
            return redirect(url_for("auth.login"))
        session.permanent = True
        session["user_id"] = user["id"]
        session["user_name"] = user["full_name"]
        session["user_role"] = user["role"]
        if user["role"] == "student":
            return redirect(url_for("dashboard.dashboard_home"))
        elif user["role"] == "sponsor":
            return redirect(url_for("skillfund.skillfund_home"))
        else:
            return redirect(url_for("admin.admin_dasboard"))

        
        

    return render_template("login.html")
@auth.route("/verify-email", methods = ["POST"])
def verify_email():
    email = request.form["email"]
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM users WHERE email=%s",(email))
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    if not user:
        flash("Email not found", "error")
        return redirect(url_for("auth.login"))
    session["reset_email"] = email
    flash("Email verified!,reset password", "success")
    return redirect(url_for("auth.login", reset = True))
@auth.route("/reset-password", methods = ["POST"])
def reset_password():
    if "reset_email" not in session:
        flash("unauthorized password reset attempt", "error")
        return redirect(url_for("auth.login"))
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]
    if password != confirm_password:
        flash("password do not match","error")
        return redirect(url_for("auth.login"))
    new_password = generate_password_hash(password)
    email = session ["reset_email"]
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE users SET password_hash=%s WHERE email=%s", (new_password, email))
    connection.commit()
    cursor.close()
    connection.close()
    session.pop("reset_email")
    flash("password updated successful", "success")
    return redirect(url_for("auth.login"))


@auth.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))
