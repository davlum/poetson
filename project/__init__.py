# project/__init__.py
# coding=utf-8

#################
#### imports ####
#################

import os

from flask import Flask, render_template, session, app, url_for, redirect, request, flash
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import text, create_engine
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta

################
#### config ####
################

app = Flask(__name__, static_url_path='/project/static')

app.config.from_object(os.environ['APP_SETTINGS'])

####################
#### extensions ####
####################

csrf = CSRFProtect(app)
mail = Mail(app)
toolbar = DebugToolbarExtension(app)
engine = create_engine('postgresql:///postgres')

####################
#### blueprints ####
####################

from project.main.views import main_blueprint
from project.user.views import user_blueprint
app.register_blueprint(main_blueprint)
app.register_blueprint(user_blueprint)


def current_user(con, email):
    query = text("""SELECT * 
                      FROM public.usuario 
                      WHERE LOWER(gr_email)=LOWER(:email)
                         OR LOWER(pers_email)=LOWER(:email)""")
    result = con.execute(query, email=email).first()
    return result

@app.before_request
def refresh_session():
    con = engine.connect()
    if 'logged_in' in session and current_user(con, session['email']) is None and request.endpoint != 'user.logout':
        flash('Su sesión ha caducado', 'danger')
        con.close()
        return redirect(url_for('user.logout'))
    session.permanent = True
    session.modified = True
    app.permanent_session_lifetime = timedelta(minutes=30)

####################
#### flask-login ####
####################



########################
#### error handlers ####
########################


@app.errorhandler(403)
def forbidden_page(error):
    return render_template("errors/403.html"), 403


@app.errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error_page(error):
    return render_template("errors/500.html"), 500
