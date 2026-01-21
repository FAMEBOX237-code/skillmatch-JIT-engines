import logging
from flask import render_template, flash

def handle_login_error(app, error, user_message=None):
    """
    Logs technical login errors and shows a safe,
    user-friendly message.
    """

    # Log the real error for developers
    app.logger.error(f"Login error: {error}")

    # What the user sees (no technical details)
    if not user_message:
        user_message = "Login failed. Please check your details and try again."

    flash(user_message, "error")
    return render_template("login.html")
