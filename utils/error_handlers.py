from .login_limiter import limiter
from flask_limiter.errors import RateLimitExceeded
from flask import render_template, flash, request, redirect, url_for, session

@limiter.request_filter
def exempt_get_requests():
    # allow GET requests to not be counted
    return request.method == "GET"

def register_error_handlers(app):
    @app.errorhandler(429)
    def ratelimit_handler(e: RateLimitExceeded):

        # Remaining seconds until user can retry
        retry_after = int(e.retry_after) if e.retry_after else 30

        
        flash("Too many login attempts.", "error")

    

        return redirect(url_for(
            "auth.login",
            lockout_seconds=retry_after
        ))