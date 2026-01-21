from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import get_db_connection
import pymysql
import os
from utils.auth_utils import login_required
from werkzeug.utils import secure_filename


project = Blueprint("project",__name__)

@project.route("/create-project", methods=["POST"])
@login_required(role="student")
def create_project():
    
    # user_id = session["user_id"]
    project_title = request.form.get("projectTitle")
    project_description = request.form.get("projectDescription")
    funding_goal = request.form.get("fundingGoal")
    required_skills = request.form.get("requiredSkills")
    # profile_picture = request.form.get("profilePicture")
    category = request.form.getlist("category[]")

    image_file = request.files.get("projectImage")
    image_filename = None

    if image_file and image_file.filename != "":
        upload_folder = os.path.join("static", "uploads", "projects")
        os.makedirs(upload_folder, exist_ok=True)
        image_filename = secure_filename(image_file.filename)
        image_path = os.path.join(upload_folder, image_filename)
        image_file.save(image_path)
        
    if not project_title or not project_description or not funding_goal or not required_skills or not category:
        flash("All fields are required.", "error")
        return redirect(url_for("skillfund.skillfund_home"))
    user_id = session["user_id"]
    
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
    INSERT INTO project (user_id, project_title, project_description, funding_goal, required_skills, image)
    VALUES (%s, %s, %s, %s, %s, %s)
""", (
    user_id,
    project_title,
    project_description,
    funding_goal,
    required_skills,
    image_filename
))

    project_id = cursor.lastrowid
    
    for category_id in category:
         cursor.execute("""
             INSERT INTO project_category (project_id, category_id) VALUES (%s, %s)
         """, (project_id, category_id))
    connection.commit()
    cursor.close()
    connection.close()
    flash("Project submitted successfully!", "success")
    return redirect(url_for("skillfund.skillfund_home"))




