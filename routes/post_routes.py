from flask import Blueprint, request, redirect, url_for, flash, session
from database import get_db_connection
from utils.auth_utils import login_required


post = Blueprint("post", __name__)



@post.route("/create-post", methods=["POST"])
@login_required(role="student")
def create_post():
    user_id = session["user_id"] # This links the post to the correct user.
    post_type = request.form.get("postType")
    title = request.form.get("title")
    description = request.form.get("description")
    skills = request.form.getlist("skills[]")


    

    if not title or len(title) < 5:
        flash("Title must be at least 5 characters.", "error")
        return redirect(url_for("dashboard.dashboard_home"))

    if not description or len(description) < 128:
        flash("Description must be at least 128 characters.", "error")
        return redirect(url_for("dashboard.dashboard_home"))

    if not skills:
        flash("Please select at least one skill.", "error")
        return redirect(url_for("dashboard.dashboard_home"))





    # Save Post to Database
    db = get_db_connection()
    cursor = db.cursor()



    cursor.execute("""
        INSERT INTO posts (user_id, post_type, title, description)
        VALUES (%s, %s, %s, %s)
    """, (user_id, post_type, title, description))

    
    post_id = cursor.lastrowid  # VERY IMPORTANT


       # 2️⃣ Link skills
    for skill_id in skills:
        cursor.execute("""
            INSERT INTO post_skills (post_id, skill_id)
            VALUES (%s, %s)
        """, (post_id, skill_id))

    db.commit()
 
 
    cursor.close()
    db.close()



    flash("Post created successfully!", "success")
    return redirect(url_for("dashboard.dashboard_home"))