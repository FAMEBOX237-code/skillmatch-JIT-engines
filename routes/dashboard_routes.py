from flask import Blueprint, render_template, request, redirect, session, url_for, flash, session
import pymysql
from database import get_db_connection
from utils.auth_utils import login_required 
dashboard = Blueprint("dashboard",__name__)


@dashboard.route("/dashboard")
@login_required(role ="student")# these line is to proctect the dashboard route so that it should only be available to student
def dashboard_home():
    
    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    
    selected_skills = request.args.getlist("skills")
    
    # Get search query from search bar (URL query)
    search_query = request.args.get("search", "").strip()
    

    # Get post type from filters (URL query)
    post_type = request.args.get("type")
    #new post today
    cursor.execute("""
        SELECT COUNT(*) AS posts_count
        FROM posts
        WHERE DATE(created_at) = CURDATE()
    """)
    new_posts_today = cursor.fetchone()["posts_count"]
    #my collaborations (my posts)
    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM posts
        WHERE user_id = %s
    """, (session["user_id"],))
    my_posts = cursor.fetchone()["count"]

    query ="""
    SELECT
        posts.id,
        posts.post_type,
        posts.description,
        posts.title,
        posts.created_at,
        users.full_name,
        users.profile_picture
    FROM posts
    JOIN users ON posts.user_id = users.id
    """
    
    conditions=[]
    params=[]
    
    # POST TYPE filter
    if post_type in ["offer", "request"]:
        conditions.append("posts.post_type = %s")
        params.append(post_type)


    # SEARCH filter
    if search_query:
        conditions.append("""
            (posts.title LIKE %s OR posts.description LIKE %s)
        """)
        params.extend([
            f"%{search_query}%",
            f"%{search_query}%"
        ])
    
    if selected_skills:
        query+= "JOIN post_skills ON posts.id = post_skills.post_id "
        conditions.append("post_skills.skill_id IN ({})" .format( ",".join(["%s"] * len(selected_skills))))
        params.extend(selected_skills)


    if conditions:
        query+= " WHERE " + " AND ".join(conditions)
        
    query+= " ORDER BY posts.created_at DESC"
    cursor.execute(query, params)
    posts= cursor.fetchall()
    
    
    for post in posts:
        cursor.execute("""
        SELECT skills.name
        FROM skills
        JOIN post_skills ON skills.id = post_skills.skill_id
        WHERE post_skills.post_id = %s
        """, (post["id"],))
        post["skills"] =  cursor.fetchall()
    
    cursor.execute("SELECT * FROM skills")
    skills = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template("dashboard.html", new_posts_today=new_posts_today, my_posts=my_posts, posts=posts, posts_count=new_posts_today , skills=skills,selected_skills=selected_skills)




@dashboard.route("/")
def home():
    return render_template("homepage.html")
@dashboard.route("/posts/<int:post_id>/interest", methods=["POST"])
@login_required(role="student")
def express_interest(post_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO post_interests (post_id, interested_user_id)
            VALUES (%s, %s)
        """, (post_id, session["user_id"]))

        connection.commit()

    except pymysql.err.IntegrityError:
        # User already expressed interest
        pass

    cursor.close()
    connection.close()

    return redirect(url_for("dashboard.dashboard_home"))