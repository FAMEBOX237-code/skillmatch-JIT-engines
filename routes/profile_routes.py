from flask import Blueprint, abort, render_template, request, redirect, url_for, flash, session
from database import get_db_connection
import pymysql
from utils.auth_utils import login_required
from flask import jsonify



profile = Blueprint("profile", __name__)



@profile.route("/profile")
@login_required(role="student")
def profile_page():

    db = get_db_connection()
    cursor = db.cursor(pymysql.cursors.DictCursor)


    # Fetch logged-in user info
    cursor.execute("""
        SELECT id, full_name, role
        FROM users
        WHERE id = %s
    """, (session["user_id"],))
    user = cursor.fetchone()




    # Fetch accumulated rating for logged-in user
    cursor.execute("""
        SELECT
            ROUND(AVG(rating), 1) AS avg_rating,
            COUNT(*) AS review_count
        FROM ratings
        WHERE rated_user_id = %s
    """, (session["user_id"],))
    rating_data = cursor.fetchone()



    # HANDLES USERS WITH NO RATINGS YET
    avg_rating = rating_data["avg_rating"] if rating_data["avg_rating"] else 0
    review_count = rating_data["review_count"]







    #  Fetch MY posts + interested count
    cursor.execute("""
        SELECT
            posts.id,
            posts.title,
            COUNT(DISTINCT post_interests.id) AS interested_count,
            COUNT(DISTINCT tasks.id) AS task_count
        FROM posts
        LEFT JOIN post_interests
            ON posts.id = post_interests.post_id
        LEFT JOIN tasks
            ON posts.id = tasks.post_id
        WHERE posts.user_id = %s
        GROUP BY posts.id
        ORDER BY posts.created_at DESC
    """, (session["user_id"],))
    my_posts = cursor.fetchall()



     
    # Fetch ONGOING + PENDING tasks (with collaborator rating)
    cursor.execute("""
        SELECT
            t.id AS task_id,
            t.status,
            p.title,

            CASE
                WHEN t.creator_id = %s THEN u.full_name
                ELSE uc.full_name
            END AS collaborator_name,

            ROUND(AVG(r.rating), 1) AS collaborator_rating,

            t.creator_id,
            t.worker_id

        FROM tasks t
        JOIN posts p ON t.post_id = p.id
        JOIN users u ON u.id = t.worker_id
        JOIN users uc ON uc.id = t.creator_id

        LEFT JOIN ratings r
            ON r.rated_user_id =
                CASE
                    WHEN t.creator_id = %s THEN t.worker_id
                    ELSE t.creator_id
                END

        WHERE (t.creator_id = %s OR t.worker_id = %s)
        AND t.status IN ('ongoing', 'completed_pending')

        GROUP BY t.id
    """, (
        session["user_id"],
        session["user_id"],
        session["user_id"],
        session["user_id"]
    ))

    ongoing_tasks = cursor.fetchall()



    # Fetch COMPLETED tasks (with collaborator rating)
    cursor.execute("""
        SELECT
            t.id AS task_id,
            t.status,
            p.title,

            CASE
                WHEN t.creator_id = %s THEN u.full_name
                ELSE uc.full_name
            END AS collaborator_name,

            ROUND(AVG(r.rating), 1) AS collaborator_rating

        FROM tasks t
        JOIN posts p ON t.post_id = p.id
        JOIN users u ON u.id = t.worker_id
        JOIN users uc ON uc.id = t.creator_id

        LEFT JOIN ratings r
            ON r.rated_user_id =
                CASE
                    WHEN t.creator_id = %s THEN t.worker_id
                    ELSE t.creator_id
                END

        WHERE (t.creator_id = %s OR t.worker_id = %s)
        AND t.status = 'completed'

        GROUP BY t.id
    """, (
        session["user_id"],
        session["user_id"],
        session["user_id"],
        session["user_id"]
    ))

    completed_tasks = cursor.fetchall()







    task_to_rate = None
    rate_task_id = request.args.get('rate_task_id')
    
    if rate_task_id:
        
        cursor.execute("""
            SELECT t.id AS task_id, p.title, u.full_name AS worker_name, t.worker_id
            FROM tasks t
            JOIN posts p ON t.post_id = p.id
            JOIN users u ON u.id = t.worker_id
            WHERE t.id = %s AND t.creator_id = %s AND t.status = 'completed_pending'
        """, (rate_task_id, session["user_id"]))
        task_to_rate = cursor.fetchone()
        cursor.close()
        db.close()

    return render_template(
        "profilepage.html",
        user=user,
        avg_rating=avg_rating,
        review_count=review_count,
        my_posts=my_posts,
        ongoing_tasks=ongoing_tasks,
        completed_tasks=completed_tasks,
        task_to_rate=task_to_rate  
    )







@profile.route("/post/<int:post_id>/interests", methods=["GET"])
@login_required(role="student")
def manage_interests(post_id):

    db = get_db_connection()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    # Confirm post belongs to logged-in user
    cursor.execute("""
        SELECT id, title, user_id
        FROM posts
        WHERE id = %s
    """, (post_id,))
    post = cursor.fetchone()

    if not post or post["user_id"] != session["user_id"]:
        cursor.close()
        db.close()
        abort(403)

    #  Fetch interested users
    cursor.execute("""
        SELECT
            pi.id AS interest_id,
            pi.status,
            u.id AS user_id,
            u.full_name
        FROM post_interests pi
        JOIN users u ON u.id = pi.interested_user_id
        WHERE pi.post_id = %s
    """, (post_id,))
    interests = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "manage_interests.html",
        post=post,
        interests=interests
    )







# Accept a collaborator for a post
@profile.route("/post/accept-interest", methods=["POST"])
@login_required(role="student")
def accept_interest():
    interest_id = request.form.get("interest_id")
    post_id = request.form.get("post_id")

    if not interest_id or not post_id:
        flash("Invalid request.", "error")
        return redirect(url_for("profile.profile_page"))

    db = get_db_connection()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    #  Get interest
    cursor.execute("""
        SELECT id, post_id, interested_user_id, status
        FROM post_interests
        WHERE id = %s
    """, (interest_id,))
    interest = cursor.fetchone()

    if not interest or interest["status"] != "pending":
        cursor.close()
        db.close()
        flash("Interest no longer available.", "error")
        return redirect(url_for("profile.profile_page"))

    #  Verify post ownership
    cursor.execute("""
        SELECT id, user_id, is_active
        FROM posts
        WHERE id = %s
    """, (interest["post_id"],))
    post = cursor.fetchone()

    if not post or post["user_id"] != session["user_id"]:
        cursor.close()
        db.close()
        abort(403)

    #  CHECK IF TASK ALREADY EXISTS (IMPORTANT FIX)
    cursor.execute("""
        SELECT id FROM tasks WHERE post_id = %s
    """, (post["id"],))
    existing_task = cursor.fetchone()

    if existing_task:
        cursor.close()
        db.close()
        flash("This post already has an ongoing collaboration.", "error")
        return redirect(url_for("profile.profile_page"))

    #  Lock post
    cursor.execute("""
        UPDATE posts
        SET is_active = 0
        WHERE id = %s
    """, (post["id"],))

    #  Accept selected interest
    cursor.execute("""
        UPDATE post_interests
        SET status = 'accepted'
        WHERE id = %s
    """, (interest_id,))

    #  Reject all other interests
    cursor.execute("""
        UPDATE post_interests
        SET status = 'rejected'
        WHERE post_id = %s AND id != %s
    """, (post["id"], interest_id))

    #  Create task
    cursor.execute("""
        INSERT INTO tasks (post_id, creator_id, worker_id)
        VALUES (%s, %s, %s)
    """, (
        post["id"],
        session["user_id"],
        interest["interested_user_id"]
    ))

    db.commit()
    cursor.close()
    db.close()

    flash("Collaborator accepted. Task is now ongoing.", "success")
    return redirect(url_for("profile.profile_page"))













@profile.route("/tasks/<int:task_id>/complete", methods=["POST"])
@login_required(role="student")
def mark_task_complete(task_id):

    db = get_db_connection()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    #  Get task
    cursor.execute("""
        SELECT id, worker_id, status
        FROM tasks
        WHERE id = %s
    """, (task_id,))
    task = cursor.fetchone()

    if not task:
        flash("Task not found or you are not authorized.", "error")
        return redirect(url_for("profile.profile_page"))

    #  Only WORKER can mark complete
    if task["worker_id"] != session["user_id"]:
        cursor.close()
        db.close()
        abort(403)

    # Task must be ongoing
    if task["status"] != "ongoing":
        flash("This task is already completed or awaiting confirmation.", "info")
        return redirect(url_for("profile.profile_page"))

    #  Update status (pending owner confirmation)
    cursor.execute("""
        UPDATE tasks
        SET status = 'completed_pending'
        WHERE id = %s
    """, (task_id,))

    db.commit()
    cursor.close()
    db.close()

    flash("Task marked as completed. Waiting for owner confirmation.", "success")
    return redirect(url_for("profile.profile_page"))









# show rating form
@profile.route("/tasks/<int:task_id>/rate", methods=["GET", "POST"])
@login_required(role="student")
def rate_task(task_id):

    db = get_db_connection()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    # Always load the task
    cursor.execute("""
        SELECT
            t.id AS task_id,
            t.creator_id,
            t.worker_id,
            t.status,
            p.title,
            u.full_name AS worker_name
        FROM tasks t
        JOIN posts p ON t.post_id = p.id
        JOIN users u ON u.id = t.worker_id
        WHERE t.id = %s
    """, (task_id,))
    task = cursor.fetchone()

    if not task:
        abort(404)

    # Only owner can rate
    if task["creator_id"] != session["user_id"]:
        abort(403)

    # ====== GET → SHOW MODAL ======
    if request.method == "GET":
        # Just redirect back to profile with the ID in the URL
        return redirect(url_for("profile.profile_page", rate_task_id=task_id))

        

    # ====== POST → SAVE RATING ======
    rating = request.form.get("rating")
    review = request.form.get("review", "")

    if not rating:
        flash("Please select a rating.", "error")
        return redirect(url_for("profile.rate_task", task_id=task_id))

    cursor.execute("""
        INSERT INTO ratings (task_id, rater_id, rated_user_id, rating, review)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        task_id,
        session["user_id"],
        task["worker_id"],
        rating,
        review
    ))

    cursor.execute("""
        UPDATE tasks
        SET status = 'completed'
        WHERE id = %s
    """, (task_id,))

    db.commit()
    cursor.close()
    db.close()

    flash("Task completed and rated successfully.", "success")
    return redirect(url_for("profile.profile_page"))
