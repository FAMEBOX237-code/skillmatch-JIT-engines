from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                flash("Please login to continue.", "error")
                return redirect(url_for("auth.login"))

            if role and session.get("user_role") != role:
                flash("Unauthorized access.", "error")
                return redirect(url_for("auth.login"))

            return f(*args, **kwargs)
        return wrapped
    return decorator
