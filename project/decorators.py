# project/decorators.py


from functools import wraps

from flask import flash, redirect, url_for, session


def check_confirmed(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not session['confirmed']:
            flash('Please confirm your account!', 'warning')
            return redirect(url_for('user.unconfirmed'))
        return func(*args, **kwargs)

    return decorated_function


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


def is_mod(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'permission' in session and session['permission'] == 'MOD':
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, You do not have permission to access this page', 'danger')
            return redirect(url_for('login'))
    return wrap


def is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'permission' in session and session['permission'] == 'ADMIN':
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, You do not have permission to access this page', 'danger')
            return redirect(url_for('login'))
    return wrap