import email
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, request
from database import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
from utils.login_limiter import limiter
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
        
@auth.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per 30 seconds" , error_message="Too many login attempts. Please wait before trying again.")
def login():
    lockout_seconds = request.args.get("lockout_seconds", type=int)
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
            flash("Your Account is Suspended! Please contact support" , "error")
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
            return redirect(url_for("admin.admin_dashboard"))



    return render_template("login.html", lockout_seconds=lockout_seconds)

@auth.route("/verify-email" , methods=["POST"])
def verify_email():
    email = request.form["email"]

    connection = get_db_connection()
    cursor = connection.cursor()
    
    
    cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()

    if not user:
        flash("Email NOt Found" ,"error")
        return redirect(url_for("auth.login"))
    
    session["reset_email"] = email
    flash("Email Verified!, Reset Password" , "success")
    return redirect(url_for("auth.login", reset = True))

@auth.route("/reset_password" , methods=["POST"])
def rest_password():
    
    if "reset_email" not in session:
        flash("Unauthorized Password Reset Attempt" , "error")
        return redirect(url_for("auth.login"))

    password = request.form["password"]
    confirm_password = request.form["confirm_password"]

    if password != confirm_password:
        flash("Password Do not Match", "error")
        return redirect(url_for("auth.login"))
    
    new_password = generate_password_hash(password)
    email = session["reset_email"]

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE users SET password_hash=%s WHERE email=%s", (new_password, email))
    connection.commit()
    cursor.close()
    connection.close()
    session.pop("reset_email")
    flash("Password Updated Successfully!" , "success")
    return redirect(url_for("auth.login"))

@auth.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully." , "success")
    return redirect(url_for("auth.login"))

@auth.route("/about_us")
def about_us():
    return render_template("about.html")