# project/user/views.py
# coding=utf-8

#################
#### imports ####
#################


import os
from project import app
from flask import render_template, Blueprint, url_for, \
    redirect, flash, request, session, abort
from werkzeug.utils import secure_filename
from sqlalchemy import text
from project.token import generate_confirmation_token, confirm_token, ts
from project import engine
from passlib.hash import bcrypt
from .forms import LoginForm, RegisterForm, \
    ChangePasswordForm, EmailForm, PasswordForm, InstrForm, \
    InfoForm, AddEntityForm, AddTrackForm, UpdateEntityForm, AddCompForm, SerieForm
from project.decorators import check_confirmed, is_admin, is_logged_in, is_mod, is_author
from project.util import current_user, current_ag, current_pers, send_email, allowed_file

from project.user.models import query_perfil, query_pers_ag, populate_info, update_info, \
    insert_part, populate_poner_ag, populate_poner_pers, update_poner_ag, update_poner_pers, delete_part, \
    init_comps, init_pistas, init_pers, init_ags, insert_comp,  insert_pista, \
    populate_pais_form, populate_comps_form, populate_comp, populate_pista, delete_comp, \
    delete_pista, insert_inst, insert_serie, delete_inst, delete_serie, populate_inst_fam, \
    add_part_choices, add_comp_choices, add_pista_choices, add_info_choices


user_blueprint = Blueprint('user', __name__,)


# a few utility functions that reside in views due to circular dependency
def init_session(con, email):
    user = current_ag(con, email)
    if user is None:
        user = current_pers(con, email)
        session['is_person'] = True
    else:
        session['is_person'] = False
    session['logged_in'] = True
    session['id'] = user.part_id
    session['confirmed'] = user.confirmado
    session['permission'] = user.permiso
    session['email'] = user.email

    # get a list of composicions by this user
    session['comps'] = init_comps(con, user.part_id)
    # list of persona added
    session['parts'] = init_pers(con, user.part_id) + init_ags(con, user.part_id)
    # list of pista_son added
    session['pistas'] = init_pistas(con, user.part_id)


def delete_wrapper(fun, con, row_id):
    try:
        fun(con, row_id)
        init_session(con, session['email'])
        flash('la eliminación se ha realizado correctamente.', 'success')
    except:
        if app.config['DEBUG']:
            raise  # Only for development
        flash('Ocurrió un error.', 'danger')


def upsert_wrapper(fun, con, form, row_id=None):
    trans = con.begin()
    try:
        if row_id is not None:
            fun(con, form, session['id'], row_id)
        else:
            fun(con, form, session['id'])
        trans.commit()
        flash('La actualización se ha realizado correctamente.', 'success')
    except:
        trans.rollback()
        if app.config['DEBUG']:
            raise  # Only for development
        flash('Ocurrió un error.', 'danger')


# The views start here

@user_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data.strip(' ')
        nom_usuario = form.nom_usuario.data.strip(' ')
        contrasena = bcrypt.using(rounds=13).hash(str(form.contrasena.data))
        con = engine.connect()
        if form.user_type.data == 'persona':
            user_query = text("""INSERT INTO public.us_pers (email, nom_usuario, contrasena) VALUES 
                          (:email, :nom_usuario, :contrasena);""")
            con.execute(user_query, email=email, nom_usuario=nom_usuario, contrasena=contrasena)
        else:
            user_query = text("""INSERT INTO public.us_ag (email, nom_usuario, contrasena) VALUES 
                          (:email, :nom_usuario, :contrasena);""")
            con.execute(user_query, email=email, nom_usuario=nom_usuario, contrasena=contrasena)
        # set session data
        init_session(con, email)
        con.close()
        token = generate_confirmation_token(email)
        confirm_url = url_for('user.confirm_email', token=token, _external=True)
        html = render_template('user/activate.html', confirm_url=confirm_url)
        subject = "Por favor, confirma tu email"
        send_email(email, subject, html)
        flash('Te has registrado y ahora estás conectado. ¡Bienvenido!', 'success')

        return redirect(url_for('user.info'))
    return render_template('user/register.html', form=form)


@user_blueprint.route('/info', methods=['GET', 'POST'])
@is_logged_in
def info():
    form = InfoForm(request.form)
    con = engine.connect()
    if request.method == 'GET':
        # prepopulate
        populate_info(con, form)
    con = engine.connect()
    add_info_choices(con, form)
    con.close()
    if request.method == 'POST' and form.validate():
        con = engine.connect()
        upsert_wrapper(update_info, con, form)
        return redirect(url_for('user.perfil'))
    return render_template('user/info.html', form=form)


@user_blueprint.route('/confirm/<token>')
@is_logged_in
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('El enlace de confirmación no es válido o ha caducado.', 'danger')
    con = engine.connect()
    init_session(con, email)
    if session['confirmed']:
        flash('Cuenta ya confirmada. Por favor Iniciar sesión.', 'success')
    else:
        confirm_user = text("""UPDATE public.usuario
                                  SET confirmado=TRUE
                                    , fecha_confirmado=now() 
                                  WHERE usuario_id=:id""")
        con.execute(confirm_user, id=session['id'])
        session['confirmed'] = True
        flash('Has confirmado tu cuenta. ¡Gracias!', 'success')
    con.close()
    return redirect(url_for('user.perfil'))


@user_blueprint.route('/reset', methods=["GET", "POST"])
def reset():
    form = EmailForm(request.form)
    if request.method == 'POST' and form.validate():
        con = engine.connect()
        user = current_user(con, form.email.data)
        con.close()
        subject = "Reajuste de contraseña solicitado"

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

    if request.method == 'POST' and form.validate():
        con = engine.connect()
        user = current_user(con, email)
        if user and user.confirmado:
            password = bcrypt.using(rounds=13).hash(str(form.password.data))
            reset_pass = text("""UPDATE public.usuario SET contrasena=:password 
                                  WHERE usuario_id=:id""")
            con.execute(reset_pass, id=user.part_id, password=password)
        con.close()
        flash('Este correo electrónico no está registrado.', 'danger')
        return redirect(url_for('signin'))
    return render_template('reset_with_token.html', form=form, token=token)


@user_blueprint.route('/resend')
@is_logged_in
def resend_confirmation():
    token = generate_confirmation_token(session['email'])
    confirm_url = url_for('user.confirm_email', token=token, _external=True)
    html = render_template('user/activate.html', confirm_url=confirm_url)
    subject = "Por favor, confirma tu email"
    send_email(session['email'], subject, html)
    flash('Se ha enviado un nuevo correo electrónico de confirmación.', 'success')
    return redirect(url_for('user.unconfirmed'))


@user_blueprint.route('/unconfirmed')
@is_logged_in
def unconfirmed():
    if session['confirmed'] is True:
        return redirect(url_for('user.perfil'))
    flash('¡Por favor, confirme su cuenta!', 'warning')
    return render_template('user/unconfirmed.html')


@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        con = engine.connect()
        init_session(con, form.email.data)
        con.close()
        flash('Ahora está conectado', 'success')
        return redirect(url_for('user.perfil'))
    return render_template('user/login.html', form=form)


@user_blueprint.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('Usted fue desconectado.', 'success')
    return redirect(url_for('user.login'))


@user_blueprint.route('/perfil', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
def perfil():
    con = engine.connect()
    if session['is_person']:
        user = current_pers(con, session['email'])
    else:
        user = current_ag(con, session['email'])
    pers_ag = query_pers_ag(con, session['id'])
    perf = query_perfil(con, session['id'])
    con.close()
    password_form = ChangePasswordForm(request.form)
    if request.method == 'POST' and password_form.validate():
        if user and bcrypt.verify(password_form.old_password.data, user.contrasena):
            con = engine.connect()
            password = bcrypt.using(rounds=13).hash(str(password_form.new_password.data))
            reset_pass = text("""UPDATE public.usuario SET contrasena=:password 
                                  WHERE usuario_id=:id""")
            con.execute(reset_pass, id=user.part_id, password=password)
            con.close()
            flash('Contraseña cambiada correctamente.', 'success')
        else:
            flash('El cambio de contraseña no tuvo éxito.', 'danger')
        return redirect(url_for('user.perfil', _anchor='tab_contrasena'))
    return render_template('user/perfil.html', user=user
                                              , perf=perf
                                              , pers_ag=pers_ag
                                              , password_form=password_form)


@user_blueprint.route('/poner/part', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
def poner_part():
    form = AddEntityForm(request.form)
    con = engine.connect()
    add_part_choices(con, form)
    con.close()
    if request.method == 'POST' and form.validate():
        con = engine.connect()
        upsert_wrapper(insert_part, con, form)
        return redirect(url_for('user.perfil', _anchor='tab_part'))
    return render_template('poner/part.html', form=form)


@user_blueprint.route('/poner/pers/<int:obra_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_author
def poner_pers(obra_id):
    form = UpdateEntityForm(request.form)
    con = engine.connect()
    if request.method == 'GET':
        populate_poner_pers(con, form, obra_id)
    add_part_choices(con, form)
    con.close()
    if request.method == 'POST' and form.validate():
        con = engine.connect()
        upsert_wrapper(update_poner_pers, con, form, obra_id)
        con.close()
        return redirect(url_for('user.perfil', _anchor='tab_part'))
    return render_template('poner/pers.html', form=form)


@user_blueprint.route('/poner/ag/<int:obra_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_author
def poner_ag(obra_id):
    form = UpdateEntityForm(request.form)
    con = engine.connect()
    if request.method == 'GET':
        populate_poner_ag(con, form, obra_id)
    add_part_choices(con, form)
    con.close()
    if request.method == 'POST' and form.validate():
        con = engine.connect()
        upsert_wrapper(update_poner_ag, con, form, obra_id)
        return redirect(url_for('user.perfil', _anchor='tab_part'))
    return render_template('poner/ag.html', form=form)


@user_blueprint.route('/remove/part/<int:obra_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_author
def remove_part(obra_id):
    con = engine.connect()
    delete_wrapper(delete_part, con, obra_id)
    con.close()
    return redirect(url_for('user.perfil', _anchor='tab_part'))


@user_blueprint.route('/remove/comp/<int:obra_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_author
def remove_comp(obra_id):
    con = engine.connect()
    delete_wrapper(delete_comp, con, obra_id)
    con.close()
    return redirect(url_for('user.perfil', _anchor='tab_pista'))


@user_blueprint.route('/remove/pista/<int:obra_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_author
def remove_pista(obra_id):
    con = engine.connect()
    delete_wrapper(delete_pista, con, obra_id)
    con.close()
    return redirect(url_for('user.perfil', _anchor='tab_pista'))



@user_blueprint.route('/poner/comp', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
def poner_comp():
    form = AddCompForm(request.form)
    con = engine.connect()
    add_comp_choices(con, form)
    con.close()
    if request.method == 'POST' and form.validate():
        con = engine.connect()
        upsert_wrapper(insert_comp, con, form)
        con.close()
        return redirect(url_for('user.perfil', _anchor='tab_pista'))
    return render_template('poner/comp.html', form=form)


@user_blueprint.route('/poner/pista', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
def poner_pista():
    form = AddTrackForm(request.form)
    con = engine.connect()
    add_pista_choices(con, form)
    con.close()
    if request.method == 'POST' and form.validate():
        if 'archivo' not in request.files:
            flash('Ninguna parte del archivo', 'danger')
            return redirect(request.url)
        file = request.files['archivo']
        if file.filename == '':
            flash('Ningún archivo seleccionado', 'danger')
            return redirect(request.url)
        if not file or not allowed_file(file.filename):
            flash('Este tipo de archivo no es aceptado', 'danger')
            return redirect(request.url)
        con = engine.connect()
        trans = con.begin()
        try:
            insert_pista(con, form, session['id'])
            trans.commit()
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('La actualización se ha realizado correctamente.', 'success')
            init_session(con, session['email'])
        except:
            trans.rollback()
            if app.config['DEBUG']:
                raise  # Only for development
            flash('Ocurrió un error.', 'danger')
        con.close()
        return redirect(url_for('user.perfil', _anchor='tab_pista'))
    return render_template('poner/pista.html', form=form)


@user_blueprint.route('/poner/comp/<int:obra_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_author
def update_comp(obra_id):
    form = AddCompForm(request.form)
    con = engine.connect()
    if request.method == 'GET':
        populate_comp(con, form, obra_id)
    add_comp_choices(con, form)
    con.close()
    if request.method == 'POST' and form.validate():
        con = engine.connect()
        upsert_wrapper(update_comp, con, form, obra_id)
        con.close()
        return redirect(url_for('user.perfil', _anchor='tab_pista'))
    return render_template('poner/comp.html', form=form)


@user_blueprint.route('/poner/pista/<int:obra_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_author
def update_pista(obra_id):
    form = AddTrackForm(request.form)
    con = engine.connect()
    if request.method == 'GET':
        populate_pista(con, form, obra_id)
    add_pista_choices(con, form)
    con.close()
    if request.method == 'POST' and form.validate():
        con = engine.connect()
        trans = con.begin()
        try:
            update_pista(con, form, obra_id, session['id'])
            trans.commit()
            flash('La actualización se ha realizado correctamente.', 'success')
            init_session(con, session['email'])
        except:
            trans.rollback()
            if app.config['DEBUG']:
                raise  # Only for development
            flash('Ocurrió un error.', 'danger')
        con.close()
        return redirect(url_for('user.perfil', _anchor='tab_pista'))
    return render_template('poner/pista.html', form=form)


@user_blueprint.route('/poner/serie', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
def poner_serie():
    form = SerieForm(request.form)
    con = engine.connect()
    form.pais.choices = populate_pais_form(con)
    con.close()
    if request.method == 'POST' and form.validate():
        con = engine.connect()
        upsert_wrapper(insert_serie, con, form)
        con.close()
        return redirect(url_for('user.perfil', _anchor='tab_pista'))
    return render_template('poner/serie.html', form=form)


@user_blueprint.route('/poner/inst', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
def poner_inst():
    form = InstrForm(request.form)
    con = engine.connect()
    form.familia_instr_id.choices = populate_inst_fam(con)
    con.close()
    if request.method == 'POST' and form.validate():
        con = engine.connect()
        upsert_wrapper(insert_inst, con, form)
        con.close()
        return redirect(url_for('user.perfil', _anchor='tab_pista'))
    return render_template('poner/inst.html', form=form)


@user_blueprint.route('/remove/serie/<int:obra_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
def remove_serie(obra_id):
    con = engine.connect()
    delete_wrapper(delete_serie, con, obra_id)
    con.close()
    return redirect(url_for('user.perfil', _anchor='tab_pista'))


@user_blueprint.route('/remove/inst/<int:obra_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
def remove_inst(obra_id):
    con = engine.connect()
    delete_wrapper(delete_inst, con, obra_id)
    con.close()
    return redirect(url_for('user.perfil', _anchor='tab_pista'))


@user_blueprint.route('/perfil/admin', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_admin
def admin():
    return render_template('user/admin.html')


@user_blueprint.route('/mod', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_mod
def mod():
    con = engine.connect()
    perf = query_perfil(con, session['id'], session['permission'])
    con.close()
    if request.method == 'POST':
        return redirect(url_for('user.mod', _anchor='tab_contrasena'))
    return render_template('user/mod.html', perf=perf)
