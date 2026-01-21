import logging
from flask import render_template

def init_error_handling(app):
    """
    This function attaches global error handlers
    to the existing Flask app.
    """

    # Log errors to a file
    logging.basicConfig(
        filename='error.log',
        level=logging.ERROR,
        format='%(asctime)s %(levelname)s: %(message)s'
    )

    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        logging.error(f"Internal server error: {error}")
        return render_template('error.html'), 500