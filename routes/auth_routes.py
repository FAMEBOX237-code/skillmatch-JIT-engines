import pymysql
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection

auth = Blueprint("auth", __name__)
# this creates  an app just for authentification routes





#REGISTRATION LOGIC (connected to register.html form)
@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form["name"] # get name from input field
        email = request.form["email"]
        skills = request.form["skills"]
        raw_password = request.form["password"]
        confirm_password = request.form["confirm-password"]
        role = request.form["role"]

        # Check if passwords match
        if raw_password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("auth.register"))

        password_hash = generate_password_hash(raw_password) 

        db = get_db_connection()
        cursor = db.cursor()

        # Check if email exists
        cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Email already exists", "error") 
            return redirect(url_for("auth.register"))

        cursor.execute("""
            INSERT INTO users (full_name, email, password_hash, role, skills)
            VALUES (%s, %s, %s, %s, %s)
        """, (full_name, email, password_hash, role, skills))
        db.commit()
        
        
        cursor.close()
        db.close()

        flash("Account created successfully!", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")








#LOGIN LOGIC (connected to login.html form)
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db_connection()
        cursor = db.cursor(pymysql.cursors.DictCursor) # to get results as dictionaries 

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        cursor.close()
        db.close()

        # Check if user exists and password is correct.
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password", "error")
            return redirect(url_for("auth.login"))


        # Check account status
        if user["status"] != "active":
            flash("Your account is suspended. Contact support.", "error")
            return redirect(url_for("auth.login"))


        # Login successful — create session
        session.permanent = True # make session permanent (lasts for app.permanent_session_lifetime)
        session["user_id"] = user["id"]
        session["user_name"] = user["full_name"]
        session["user_role"] = user["role"] # maeans we can show/hide parts of the ui pages based on role (e.g admin dashboard)

        
        flash("Login successful!", "success")
        
        # Redirect based on role
        if user["role"] == "student":
            return redirect(url_for("dashboard.dashboard_home"))
        elif user["role"] == "sponsor":
            return redirect("/skillfund")
        else:
            return redirect(url_for("admin.admin_dashboard"))

    return render_template("login.html")







#EMAIL VERIFICATION LOGIC (connected to verify_email modal in login.html)
@auth.route("/verify-email", methods=["POST"])
def verify_email():
    email = request.form["email"]

    db = get_db_connection()
    cursor = db.cursor()
    
    cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()

    cursor.close()
    db.close()

    if not user:
        flash("Email not found", "error")
        return redirect(url_for("auth.login"))
    
    # Store verified email temporarily
    session["reset_email"] = email

    flash("Email verified. Reset password.", "success")
    return redirect(url_for("auth.login", reset="true"))




# PASSWORD RESET LOGIC (connected to reset_password modal in login.html)
@auth.route("/reset-password", methods=["POST"])
def reset_password():
    if "reset_email" not in session:
        flash("Unauthorized password reset attempt.", "error")
        return redirect(url_for("auth.login"))
    
    password = request.form["password"]
    confirm = request.form["confirm_password"]

    if password != confirm:
        flash("Passwords do not match", "error")
        return redirect(url_for("auth.login"))
    
    new_password = generate_password_hash(password)
    email = session["reset_email"]

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE users SET password_hash=%s WHERE email=%s",
        (new_password, email)
    )
    db.commit()

    cursor.close()
    db.close()

    session.pop("reset_email")  # cleanup

    flash("Password updated successfully!", "success")
    return redirect(url_for("auth.login"))



# LOGOUT LOGIC
@auth.route("/logout")
def logout():
    session.clear()  # removes all session data
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("auth.login"))

