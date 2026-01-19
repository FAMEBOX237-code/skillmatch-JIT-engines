from routes.auth_routes import auth
from flask import Flask
from routes.dashboard_routes import dashboard
from routes.post_routes import post
from datetime import timedelta
from utils.time_helpers import time_since


app = Flask(__name__)
app.secret_key="skillmatch_secret_key"
app.jinja_env.filters["time_since"] = time_since

app.permanent_session_lifetime = timedelta(days=1)
app.register_blueprint(dashboard)
app.register_blueprint(auth)
app.register_blueprint(post)

@app.after_request
def disable_caching(response):
    response.headers["Cache-control"] = "no-store, no-cache, must-revalidate,  private"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == "__main__":
    app.run(debug=True)
