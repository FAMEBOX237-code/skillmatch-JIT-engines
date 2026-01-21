from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import get_db_connection
from utils.auth_utils import login_required
import pymysql


skillfund = Blueprint("skillfund", __name__)

@skillfund.route("/skillfund")
@login_required(role=["student", "sponsor"])
def skillfund_home():
    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # Fetch categories for filters & form
    cursor.execute("SELECT id, name FROM category ORDER BY name")
    categories = cursor.fetchall()

    # Read filters
    selected_categories = request.args.getlist("category")
    sort = request.args.get("sort", "newest")
    search_query = request.args.get("q", "").strip()  

    # Base query
    query = """
        SELECT 
            p.id,
            p.project_title,
            p.project_description,
            p.funding_goal,
            p.required_skills,
            p.image,
            GROUP_CONCAT(c.name SEPARATOR ', ') AS categories
        FROM project p
        JOIN project_category pc ON p.id = pc.project_id
        JOIN category c ON pc.category_id = c.id
    """
    conditions = []
    params = []

    #  Search filter
    if search_query:
        conditions.append(
            "(p.project_title LIKE %s OR p.project_description LIKE %s OR p.required_skills LIKE %s)"
        )
        like_value = f"%{search_query}%"
        params.extend([like_value, like_value, like_value])

    #  Category filter
    if selected_categories:
        placeholders = ",".join(["%s"] * len(selected_categories))
        conditions.append(f"c.id IN ({placeholders})")
        params.extend(selected_categories)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " GROUP BY p.id"

    #  Sorting
    if sort == "title":
        query += " ORDER BY p.project_title ASC"
    elif sort == "funding":
        query += " ORDER BY p.funding_goal DESC"
    else:
        query += " ORDER BY p.id DESC"

    cursor.execute(query, params)
    projects = cursor.fetchall()

    # Fetch logged-in user details
    cursor.execute("""
    SELECT id, full_name, profile_picture, email
    FROM users
    WHERE id = %s
    """, (session["user_id"],))
    current_user = cursor.fetchone()


    cursor.close()
    connection.close()

    return render_template(
        "skillfund.html",
        category=categories,
        projects=projects,
        selected_categories=selected_categories,
        sort=sort,
        search_query=search_query,
        current_user=current_user
    )
