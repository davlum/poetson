# project/user/views.py


#################
#### imports ####
#################

from flask import render_template, Blueprint, url_for, \
    redirect, flash, request, session, abort, app,
from flask_login import login_user, logout_user, \
    is_logged_in, current_user
from sqlalchemy import text
from project.util import send_email
from project.token import generate_confirmation_token, confirm_token, ts
from project import db, bcrypt
from .forms import LoginForm, RegisterForm, ChangePasswordForm, EmailForm, PasswordForm
from project.decorators import check_confirmed, is_admin, is_logged_in, is_mod



################
#### config ####
################

user_blueprint = Blueprint('user', __name__,)


################
#### routes ####
################


def user_query(email):
    query = text("""SELECT * FROM part_us WHERE email=:email""")
    return db.engine.execute(query, email=email).first_or_404()


def init_session(user_result):
    session['logged_in'] = True
    session['confirmed'] = user_result.confirmado
    if user_result.permiso == 'ADMIN':
        session['permission'] = 'ADMIN'
    elif user_result.permiso == 'MOD':
        session['permission'] = 'MOD'
    else:
        session['permission'] = 'EDITOR'
    session['email'] = user_result.email


@user_blueprint.route('/reset', methods=["GET", "POST"])
def reset():
    form = EmailForm()
    if form.validate_on_submit():
        user = user_query(form.email.data)

        subject = "Password reset requested"

        # Here we use the URLSafeTimedSerializer we created in `util` at the
        # beginning of the chapter
        token = ts.dumps(user.email, salt='recover-key')

        recover_url = url_for(
            'reset_with_token',
            token=token,
            _external=True)

        html = render_template(
            'email/recover.html',
            recover_url=recover_url)

        # Let's assume that send_email was defined in myapp/util.py
        send_email(user.email, subject, html)

        return redirect(url_for('index'))
    return render_template('reset.html', form=form)

@user_blueprint.route('/reset/<token>', methods=["GET", "POST"])
def reset_with_token(token):
    try:
        email = ts.loads(token, salt="recover-key", max_age=86400)
    except:
        abort(404)

    form = PasswordForm()

    if form.validate_on_submit():
        user = user_query(email)
        if user and user.confirmado:
            password = bcrypt.encrypt(str(form.password.data))
            reset_pass = text("""UPDATE usario SET contrasena=:password 
                                  WHERE part_id:id""")
            db.engine.execute(reset_pass, id=user.part_id, password=password)
            return redirect(url_for('signin'))

    return render_template('reset_with_token.html', form=form, token=token)


@user_blueprint.route('/resend')
@is_logged_in
def resend_confirmation():
    token = generate_confirmation_token(session['email'])
    confirm_url = url_for('user.confirm_email', token=token, _external=True)
    html = render_template('user/activate.html', confirm_url=confirm_url)
    subject = "Please confirm your email"
    send_email(session['email'], subject, html)
    flash('A new confirmation email has been sent.', 'success')
    return redirect(url_for('user.unconfirmed'))


@user_blueprint.route('/unconfirmed')
@is_logged_in
def unconfirmed():
    if session['confirmed'] is True:
        return redirect('main.home')
    flash('Please confirm your account!', 'warning')
    return render_template('user/unconfirmed.html')


@user_blueprint.route('/confirm/<token>')
@is_logged_in
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
    user = user_query(email)
    if user.confirmado:
        flash('Account already confirmed. Please login.', 'success')
    else:
        confirm_user = text("""UPDATE usario SET confirmado=TRUE, fecha_confirmado=now() 
                                  WHERE part_id:id""")
        db.engine.execute(confirm_user, id=user.part_id)
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('main.home'))


@user_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        username = form.username.data
        password = bcrypt.encrypt(str(form.password.data))

        user_query = text("""INSERT INTO part_us (email, nom_usario, contrasena) VALUES 
                        (:email, :name, :password);""")
        user_result = db.engine.execute(user_query, email=email, name=username, password=password)

        token = generate_confirmation_token(email)
        confirm_url = url_for('user.confirm_email', token=token, _external=True)
        html = render_template('user/activate.html', confirm_url=confirm_url)
        subject = "Please confirm your email"
        send_email(email, subject, html)

        init_session(user_result)

        flash('You registered and are now logged in. Welcome!', 'success')

        return redirect(url_for('user.unconfirmed'))

    return render_template('user/register.html', form=form)


@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data.strip()
        password_candidate = form.password.data
        user = user_query(email)
        if user is not None:
            if bcrypt.verify(password_candidate, user.contrasena):
                init_session(user)
                flash('You are now logged in', 'success')
                return redirect(url_for('user/profile.html'))
            else:
                error = 'Invalid login'
                app.logger.info('PASSWORD NOT MATCHED', error=error, form=form)
        else:
            error = 'Email not found'
            return render_template('user/login.html', error=error, form=form)
    return render_template('user/login.html', form=form)


@user_blueprint.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You were logged out.', 'success')
    return redirect(url_for('user.login'))


@user_blueprint.route('/profile', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
def profile():
    form = ChangePasswordForm(request.form)
    if form.validate_on_submit():
        user = user_query(session['email'])
        if user and bcrypt.verify(form.password.data, user.contrasena):
            user.contrasena = bcrypt.generate_password_hash(form.password.data)
            password = bcrypt.encrypt(str(form.password.data))
            reset_pass = text("""UPDATE usario SET contrasena=:password 
                                  WHERE part_id:id""")
            db.engine.execute(reset_pass, id=user.part_id, password=password)
            flash('Password successfully changed.', 'success')
            return redirect(url_for('user.profile'))
        else:
            flash('Password change was unsuccessful.', 'danger')
            return redirect(url_for('user.profile'))
    return render_template('user/profile.html', form=form)
