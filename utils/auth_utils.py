from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(role=None):
    """
    role: None -> allow all logged-in users
    str -> allow one role
    list/tuple -> allow multiple roles
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                flash("Please login to continue.", "error")
                return redirect(url_for("auth.login"))

            user_role = session.get("user_role")

            # allow multiple roles
            if role:
                if isinstance(role, (list, tuple)):
                    if user_role not in role:
                        flash("Unauthorized access.", "error")
                        return redirect(url_for("auth.login"))
                else:  # single role
                    if user_role != role:
                        flash("Unauthorized access.", "error")
                        return redirect(url_for("auth.login"))

            return f(*args, **kwargs)
        return wrapped
    return decorator