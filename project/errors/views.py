# project/user/views.py
# coding=utf-8

#################
#### imports ####
#################


from project import app
from flask import render_template, Blueprint, url_for, \
    redirect, flash, request, session, abort

errors_blueprint = Blueprint('errors', __name__,)


@errors_blueprint.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@errors_blueprint.errorhandler(401)
def unauthorized(e):
    return render_template('errors/401.html'), 401

