from routes.auth_routes import auth
from flask import Flask
from routes.home_routes import home
from routes.dashboard_routes import dashboard
from utils.time_helpers import time_since
from datetime import timedelta
from routes.post_routes import post
from routes.profile_routes import profile
from routes.skillfund_routes import skillfund
from routes.project_routes import project
from utils.login_limiter import limiter
from utils.error_handlers import register_error_handlers
from utils.login_error_handler import handle_login_error
from utils.error_handler import init_error_handling
from utils.validator import validate_email, validate_password


app = Flask(__name__)
app.secret_key="skillmatch_secret_key"
app.jinja_env.filters['time_since'] = time_since

app.permanent_session_lifetime =  timedelta(days=1)  

limiter.init_app(app)
register_error_handlers(app)
app.register_blueprint(dashboard)
app.register_blueprint(auth)
app.register_blueprint(home)
app.register_blueprint(skillfund)
app.register_blueprint(project)
app.register_blueprint(post)
app.register_blueprint(profile)
init_error_handling(app)





@app.after_request
def disable_cache(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, private"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response






if __name__ == "__main__":
    app.run(debug=True)
