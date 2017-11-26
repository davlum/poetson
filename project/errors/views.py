# project/user/views.py
# coding=utf-8


from flask import render_template, Blueprint


errors_blueprint = Blueprint('errors', __name__,)


@errors_blueprint.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@errors_blueprint.errorhandler(401)
def unauthorized(e):
    return render_template('errors/401.html'), 401


@errors_blueprint.errorhandler(500)
def unauthorized(e):
    return render_template('errors/500.html'), 500

@errors_blueprint.errorhandler(429)
def unauthorized(e):
    return render_template('errors/500.html'), 429
