from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import get_db_connection
import pymysql
post = Blueprint("post", __name__)

@post.route("/create-post", methods=["POST"])
def create_post():
     if "user_id" not in session:
        flash("Please login to create a post.", "error")
        return redirect(url_for("auth.login"))
     
     post_type = request.form.get("postType")
     title = request.form.get("title")
     description = request.form.get("description")
     skills = request.form.get("skills[]")
     if not title or not description or not skills:
        flash("All fields are required.", "error")
        return redirect(url_for("dashboard.dashboard_home"))
     user_id = session["user_id"]

     connection = get_db_connection()
     cursor = connection.cursor()
     cursor.execute("""INSERT INTO posts (user_id, post_type, title, description) VALUES (%s, %s, %s, %s)
     """, (user_id, post_type, title, description))
     post_id = cursor.lastrowid

     for skill_id in skills:
         cursor.execute("""
             INSERT INTO post_skills (post_id, skill_id) VALUES (%s, %s)
         """, (post_id, skill_id))
     connection.commit()
     cursor.close()
     connection.close()
     flash("Post created successfully!", "success")
     return redirect(url_for("dashboard.dashboard_home"))






 