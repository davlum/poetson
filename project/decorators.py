# project/decorators.py


from functools import wraps

from flask import flash, redirect, url_for, session, request


def check_confirmed(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not session['confirmed']:
            return redirect(url_for('user.unconfirmed'))
        return func(*args, **kwargs)

    return decorated_function


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('No autorizado, Inicia sesión', 'danger')
            return redirect(url_for('user.login'))
    return wrap


def is_mod(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'permission' in session and (session['permission'] == 'MOD' or
                                        session['permission'] == 'ADMIN'):
            return f(*args, **kwargs)
        else:
            flash('No autorizado, No tienes permiso para acceder a esta página', 'danger')
            return redirect(url_for('user.profile'))
    return wrap


def is_author(f):
    @wraps(f)
    def wrap(part_id, *args, **kwargs):
        if 'permission' in session and (session['permission'] == 'MOD' or
                                        session['permission'] == 'ADMIN'):
            return f(part_id, *args, **kwargs)
        elif request.endpoint == 'comp' and part_id in session['comps']:
            return f(part_id, *args, **kwargs)
        elif request.endpoint == 'pista' and part_id in session['pistas']:
            return f(part_id, *args, **kwargs)
        elif request.endpoint == 'part' and part_id in session['parts']:
            return f(part_id, *args, **kwargs)
        else:
            flash('No autorizado, No tienes permiso para acceder a esta página', 'danger')
            return redirect(url_for('user.profile'))
    return wrap


def is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'permission' in session and session['permission'] == 'ADMIN':
            return f(*args, **kwargs)
        else:
            flash('No autorizado, No tienes permiso para acceder a esta página', 'danger')
            return redirect(url_for('user.profile'))
    return wrap
