from routes.auth_routes import auth 
from flask import dashboard Flask
import pymysql
from routes.post_routes import post
from routes.dashboard_routes import dashboard
from utils.time_helpers import time_since
from datetime import timedelta
from flask import error_handler 
from validators import validate_email, validate_password
from login_error_handler import handle_login_error


app = Flask(__name__)
app.secret_key="skillmatch_secret_key"
app.jinja_env.filters['time_since'] =time_since
app.init_error_handling(app)



app.permenent_session_lifetime = timedelta(days=1)

app.register_blueprint(auth)
app.register_blueprint(dashboard)
app.register_blueprint(post)


@app.after_request
def disable_cache(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, private"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


if __name__ == "__main__":
    app.run(debug=True)
