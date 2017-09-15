# project/user/views.py
# coding=utf-8

#################
#### imports ####
#################


import os, errno
from project import app
from flask import render_template, Blueprint, url_for, \
    redirect, flash, request, session, abort
from werkzeug.utils import secure_filename
from sqlalchemy import text
from project.token import generate_confirmation_token, confirm_token, ts
from project import engine
from mutagen import File
from passlib.hash import bcrypt
from .forms import LoginForm, RegisterForm, \
    ChangePasswordForm, EmailForm, PasswordForm, InstrForm, \
    InfoForm, AddEntityForm, AddTrackForm, UpdateEntityForm, AddCompForm, SerieForm
from project.decorators import check_confirmed, is_admin, is_logged_in, is_mod, is_author
from project.util import current_user, current_gr, current_pers, send_email, allowed_file

from project.user.models import query_perfil, query_pers_gr, populate_info, update_info, update_permiso, \
    insert_part, populate_poner_grupo, populate_poner_pers, update_poner_grupo, update_poner_pers, delete_part, \
    init_comps, init_pistas, init_pers, init_grupos, insert_comp,  insert_pista, query_archivos, update_prohibido, \
    populate_pais_form, populate_comp, populate_pista, delete_comp, insert_archivo, estado_comp, estado_grupo, \
    delete_pista, insert_inst, insert_serie, delete_inst, delete_serie, populate_inst_fam, estado_pers, estado_pista, \
    add_part_choices, add_comp_choices, add_pista_choices, add_info_choices, update_comp, update_pista


user_blueprint = Blueprint('user', __name__,)


# a few utility functions that reside in views due to circular dependency
def init_session(con, email):
    user = current_gr(con, email)
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
    session['parts'] = init_pers(con, user.part_id) + init_grupos(con, user.part_id)
    # list of pista_son added
    session['pistas'] = init_pistas(con, user.part_id)


def delete_wrapper(fun, con, row_id):
    try:
        fun(con, row_id)
        init_session(con, session['email'])
        flash('la eliminación se ha realizado correctamente.', 'success')
    except Exception as ex:
        if app.config['DEBUG']:
            raise  # Only for development
        flash('Ocurrió un error;' + str(ex), 'danger')


def upsert_wrapper(fun, con, form, row_id=None):
    trans = con.begin()
    try:
        if row_id is not None:
            fun(con, form, session['id'], row_id)
        else:
            fun(con, form, session['id'])
        trans.commit()
        init_session(con, session['email'])
        flash('La actualización se ha realizado correctamente.', 'success')
    except Exception as ex:
        trans.rollback()
        if app.config['DEBUG']:
            raise  # Only for development
        flash('Ocurrió un error; ' + str(ex), 'danger')


def validate_file():
    if 'archivo' not in request.files:
        return False, 'Ninguna parte del archivo'
    file = request.files['archivo']
    if file.filename == '':
        return False, 'Ningún archivo seleccionado'
    if not file or not allowed_file(file.filename):
        return False, 'Este tipo de archivo no es aceptado'
    return True, file


def upload_file(con, pista_id, file):
    audio = File(file)
    if audio is not None:
        filename = secure_filename(file.filename)
        archivo_id = str(insert_archivo(con, audio, filename, pista_id))
        path = app.config['UPLOAD_FOLDER'] + '/' + str(pista_id) + '/' + archivo_id
        file.seek(0)
        os.makedirs(path, exist_ok=True)
        file.save(os.path.join(path, filename))
        file.close()
    else:
        flash('Is not an audio file', 'danger')


#def upload_file(con, pista_id, file):
#    filename = secure_filename(file.filename)
#    path = app.config['UPLOAD_FOLDER'] + '/' + str(pista_id)
#    os.makedirs(path, exist_ok=True)
#    file.save(os.path.join(path, filename))
#    file.close()


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
            user_query = text("""INSERT INTO public.us_gr (email, nom_usuario, contrasena) VALUES 
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
        user = current_gr(con, session['email'])
    pers_gr = query_pers_gr(con, session['id'])
    result = query_perfil(con, session['id'])
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
                                              , result=result
                                              , pers_gr=pers_gr
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


@user_blueprint.route('/poner/grupo/<int:obra_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_author
def poner_grupo(obra_id):
    form = UpdateEntityForm(request.form)
    con = engine.connect()
    if request.method == 'GET':
        populate_poner_grupo(con, form, obra_id)
    add_part_choices(con, form)
    con.close()
    if request.method == 'POST' and form.validate():
        con = engine.connect()
        upsert_wrapper(update_poner_grupo, con, form, obra_id)
        return redirect(url_for('user.perfil', _anchor='tab_part'))
    return render_template('poner/grupo.html', form=form)


@user_blueprint.route('/remove/part/<int:obra_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_author
def remove_part(obra_id):
    con = engine.connect()
    delete_wrapper(delete_part, con, obra_id)
    con.close()
    return redirect(url_for('user.perfil', _anchor='tab_pista'))


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


@user_blueprint.route('/poner/comp/<int:obra_id>/', methods=['GET', 'POST'])
@user_blueprint.route('/poner/comp', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_author
def poner_comp(obra_id=None):
    form = AddCompForm(request.form)
    con = engine.connect()
    if request.method == 'GET' and obra_id is not None:
        populate_comp(con, form, obra_id)
    add_comp_choices(con, form)
    con.close()
    if request.method == 'POST' and form.validate():
        con = engine.connect()
        if obra_id is None:
            upsert_wrapper(insert_comp, con, form)
        else:
            upsert_wrapper(update_comp, con, form, obra_id)
        con.close()
        return redirect(url_for('user.perfil', _anchor='tab_pista'))
    return render_template('poner/comp.html', form=form)


def upsert_pista_wrapper(fun, con, form, file, pista_id=None):
    trans = con.begin()
    try:
        if pista_id is None:
            pista_id = str(fun(con, form, session['id']))
        else:
            fun(con, form, session['id'], pista_id)
        if file is not None:
            upload_file(con, pista_id, file)
        trans.commit()
        init_session(con, session['email'])
        flash('La actualización se ha realizado correctamente.', 'success')
    except Exception as ex:
        trans.rollback()
        if app.config['DEBUG']:
            raise   # Only for development
        flash('Ocurrió un error; ' + str(ex), 'danger')


@user_blueprint.route('/poner/pista/<int:obra_id>/', methods=['GET', 'POST'])
@user_blueprint.route('/poner/pista', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_author
def poner_pista(obra_id=None):
    result = {}
    form = AddTrackForm(request.form)
    con = engine.connect()
    if request.method == 'GET' and obra_id is not None:
        populate_pista(con, form, obra_id)
    add_pista_choices(con, form)
    result['archivos'] = query_archivos(con, obra_id)
    result['editor'] = True
    con.close()
    if request.method == 'POST' and form.validate():
        validated, file = validate_file()
        con = engine.connect()
        if obra_id is None:
            # When inserting for the first time there must be a file
            if not validated:
                flash(file, 'danger')
                return redirect(url_for('user.poner_pista'))
            upsert_pista_wrapper(insert_pista, con, form, file)
        else:
            if not validated:
                # On update a file need not be uploaded
                flash(file, 'warning')
                upsert_pista_wrapper(update_pista, con, form, file=None, pista_id=obra_id)
            else:
                upsert_pista_wrapper(update_pista, con, form, file, obra_id)
        con.close()
        return redirect(url_for('user.perfil', _anchor='tab_pista'))
    return render_template('poner/pista.html', form=form, result=result)


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


@user_blueprint.route('/estado/<obra>/<int:obra_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_mod
def estado(obra, obra_id):
    con = engine.connect()
    json = request.get_json(force=True)
    estado = json['estado'].upper()
    if 'comp' in obra:
        estado_comp(con, obra_id, estado)
    elif 'pista' in obra:
        estado_pista(con, obra_id, estado)
    elif 'pers' in obra:
        estado_pers(con, obra_id, estado)
    elif 'grupo' in obra:
        estado_grupo(con, obra_id, estado)
    con.close()
    return '', 204


@user_blueprint.route('/permiso/<int:usuario_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_admin
def permiso(usuario_id):
    con = engine.connect()
    json = request.get_json(force=True)
    permiso = json['permiso'].upper()
    update_permiso(con, usuario_id, permiso)
    con.close()
    return redirect(url_for('user.admin', _anchor='tab_usario'))


@user_blueprint.route('/prohibido/<int:usuario_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_admin
def prohibido(usuario_id):
    con = engine.connect()
    json = request.get_json(force=True)
    prohibido = (json['prohibido'] == 'True')
    update_prohibido(con, usuario_id, prohibido)
    con.close()
    return redirect(url_for('user.admin', _anchor='tab_usuario'))


@user_blueprint.route('/remove/archivo/<int:obra_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
def remove_archivo(obra_id):
    con = engine.connect()
    delete_wrapper(delete_inst, con, obra_id)
    con.close()
    return redirect(url_for('user.perfil', _anchor='tab_pista'))


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
    con = engine.connect()
    result = query_perfil(con, session['id'], session['permission'])
    con.close()
    return render_template('user/admin.html', result=result)


@user_blueprint.route('/mod', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_mod
def mod():
    con = engine.connect()
    result = query_perfil(con, session['id'], session['permission'])
    con.close()
    return render_template('user/mod.html', result=result)
