from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from utils.auth_utils import login_required
from database import get_db_connection
import pymysql



dashboard = Blueprint("dashboard", __name__)




# route to dashboard_home
@dashboard.route("/dashboard")
@login_required(role="student")
def dashboard_home():

    db = get_db_connection()
    cursor = db.cursor(pymysql.cursors.DictCursor) # to get results as dictionaries 




    # Get selected skill IDs from filters (URL query)
    selected_skills = request.args.getlist("skills")
    

    # Get search query from search bar (URL query)
    search_query = request.args.get("search", "").strip()
    

    # Get post type from filters (URL query)
    post_type = request.args.get("type")


    
   
    # Minimum rating filter (slider)
    min_rating = request.args.get("min_rating", type=float)


    sort = request.args.get("sort", "recent")







    
    # 1️⃣ New posts today
    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM posts
        WHERE DATE(created_at) = CURDATE()
    """)
    new_posts_today = cursor.fetchone()["count"]

    # 3️⃣ My collaborations (my posts)
    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM posts
        WHERE user_id = %s
    """, (session["user_id"],))
    my_posts = cursor.fetchone()["count"]

    



    


    # Base query (always valid)
    query = """
        SELECT DISTINCT
            posts.id,
            posts.user_id,
            posts.is_active,
            posts.post_type,
            posts.title,
            posts.description,
            posts.created_at,

            users.full_name,
            users.profile_picture,
            users.email,

            COALESCE(ROUND(AVG(r.rating), 1), 0) AS user_rating

        FROM posts
        JOIN users ON posts.user_id = users.id

        LEFT JOIN ratings r
            ON r.rated_user_id = users.id
    """


    conditions = []
    params = []



    having_conditions = []
    having_params = []




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


    # Apply skill filtering ONLY if skills are selected
    if selected_skills:
        query += " JOIN post_skills ON posts.id = post_skills.post_id "
        conditions.append(
            "post_skills.skill_id IN ({})".format(
                ",".join(["%s"] * len(selected_skills))
            )
        )
        params.extend(selected_skills)


    # Apply conditions if any
    if conditions:
        query += " WHERE " + " AND ".join(conditions)


    # MINIMUM RATING filter (uses HAVING, not WHERE)
    if min_rating is not None and min_rating > 0:
        having_conditions.append("AVG(r.rating) >= %s")
        having_params.append(min_rating)



    query += " GROUP BY posts.id"

    if having_conditions:
        query += " HAVING " + " AND ".join(having_conditions)

        # Sorting
    if sort == "rating_desc":
        query += " ORDER BY user_rating DESC"
    elif sort == "rating_asc":
        query += " ORDER BY user_rating ASC"
    else:
        query += " ORDER BY posts.created_at DESC"



    

    cursor.execute(query, params + having_params)
    posts = cursor.fetchall()




    
    # Fetch skills for each post, that is for eachpost, get its skills, attach them to post dictionary, post['skills']
    for post in posts:
        cursor.execute("""
            SELECT skills.name
            FROM post_skills
            JOIN skills ON post_skills.skill_id = skills.id
            WHERE post_skills.post_id = %s
        """, (post["id"],))
        post["skills"] = cursor.fetchall()   




    # Fetch all skills (used by filter ui)   
    cursor.execute("SELECT * FROM skills")
    skills = cursor.fetchall()
    

    cursor.close()
    db.close()

    return render_template(
        "dashboard.html",
        posts=posts,
        skills=skills,
        new_posts_today=new_posts_today,
        my_posts=my_posts,
        selected_skills=selected_skills
    )







@dashboard.route("/posts/<int:post_id>/interest", methods=["POST"])
@login_required(role="student")
def express_interest(post_id):
    db = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute("""
            INSERT INTO post_interests (post_id, interested_user_id)
            VALUES (%s, %s)
        """, (post_id, session["user_id"]))

        db.commit()

    except pymysql.err.IntegrityError:
        # User already expressed interest
        pass

    cursor.close()
    db.close()

    return redirect(url_for("dashboard.dashboard_home"))















