from routes.auth_routes import auth
from flask import Flask
from routes.dashboard_routes import dashboard
from utils.time_helpers import time_since
from datetime import timedelta
from routes.skillfund_routes import skillfund
from routes.project_routes import project



app = Flask(__name__)
app.secret_key="skillmatch_secret_key"
app.jinja_env.filters['time_since'] = time_since




app.permanent_session_lifetime =  timedelta(days=1)  # Set session timeout to 30 minutes



app.register_blueprint(dashboard)
app.register_blueprint(auth)
app.register_blueprint(skillfund)
app.register_blueprint(project)






@app.after_request
def disable_cache(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, private"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response






if __name__ == "__main__":
    app.run(debug=True)
