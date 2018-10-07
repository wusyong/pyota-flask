from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)

@errors.app_errorhandler(404)
@errors.app_errorhandler(403)
@errors.app_errorhandler(500)
def errorr(error):
    return render_template('errors.html', error=error), 404
