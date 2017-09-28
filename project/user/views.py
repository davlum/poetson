# project/user/views.py
# coding=utf-8


import os
from shutil import rmtree
from project import app
from flask import render_template, Blueprint, url_for, \
    redirect, flash, request, session, abort, jsonify
from werkzeug.utils import secure_filename
from sqlalchemy import text
from project.token import generate_confirmation_token, confirm_token, ts
from project import engine
from mutagen import File
from passlib.hash import bcrypt
from .forms import LoginForm, RegisterForm, \
    ChangePasswordForm, EmailForm, PasswordForm, InstrForm, GenMusForm, IdiomaForm, TemaForm, AlbumForm, \
    InfoForm, AddEntityForm, AddTrackForm, UpdateEntityForm, AddCompForm, SerieForm
from project.decorators import check_confirmed, is_admin, is_logged_in, is_mod, is_author
from project.util import current_user, current_gr, current_pers, send_email, allowed_audio_file, allowed_image_file

from project.user.models import query_perfil, query_pers_gr, populate_info, update_info, update_permiso, \
    insert_part, populate_poner_grupo, populate_poner_pers, update_poner_grupo, update_poner_pers, delete_persona, \
    init_comps, init_pistas, init_pers, init_grupos, insert_comp,  insert_pista, query_archivos, update_prohibido, \
    populate_comp, populate_pista, delete_comp, insert_archivo, estado_comp, estado_grupo, \
    delete_pista, insert_inst, insert_serie, delete_inst, delete_serie, populate_inst_fam, estado_pers, estado_pista, \
    add_part_choices, add_comp_choices, add_pista_choices, add_info_choices, update_comp, update_pista, \
    populate_instrumento_form, populate_idiomas_form, populate_serie_form, populate_gen_mus_form, populate_temas_form, \
    populate_album_form, insert_album, insert_genero, insert_idioma, insert_tema, delete_tema, delete_idioma, \
    delete_genero, delete_album, delete_grupo


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


def delete_wrapper(fun, con, row_id, usuario_id=None):
    try:
        valid = True
        if usuario_id is not None:
            valid = fun(con, row_id, usuario_id)
        else:
            fun(con, row_id)
        if valid:
            init_session(con, session['email'])
            flash('la eliminación se ha realizado correctamente.', 'success')
        else:
            flash("""No se puede borrar. Esto todavía se refiere por otra pieza de datos. 
            Elimine todos los datos que se refieren a éste antes de él.""", 'danger')
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


def insert_wrapper(fun, con, form):
    trans = con.begin()
    try:
        fun(con, form)
        trans.commit()
        flash('La actualización se ha realizado correctamente.', 'success')
    except Exception as ex:
        trans.rollback()
        if app.config['DEBUG']:
            raise  # Only for development
        flash('Ocurrió un error; ' + str(ex), 'danger')


def validate_audio_file():
    if 'archivo' not in request.files:
        return False, 'Ningún archivo seleccionado'
    file = request.files['archivo']
    if file.filename == '':
        return False, 'Ningún archivo seleccionado'
    if not file or not allowed_audio_file(file.filename):
        return False, 'Este tipo de archivo no es aceptado'
    return True, file


def validate_image_file():
    if 'archivo' not in request.files:
        return False, 'Ningún archivo seleccionado'
    file = request.files['archivo']
    if not allowed_image_file(file.filename):
        return False, 'Este tipo de archivo no es aceptado'
    return True, file


def upload_audio(con, pista_id, file):
    file.seek(0)
    audio = File(file)
    if audio is not None:
        filename = secure_filename(file.filename)
        archivo_id = str(insert_archivo(con, audio, filename, pista_id))
        path = app.config['UPLOAD_FOLDER'] + '/audio/' + str(pista_id) + '/' + archivo_id
        file.seek(0)
        os.makedirs(path, exist_ok=True)
        file.save(os.path.join(path, filename))
        file.close()
    else:
        flash('No es un archivo de audio', 'danger')


def upload_album_image(file, album_id):
    file.seek(0)
    filename = secure_filename(file.filename)
    path = app.config['UPLOAD_FOLDER'] + '/images/albums/' + str(album_id)
    os.makedirs(path, exist_ok=True)
    file.save(os.path.join(path, filename))
    file.close()


def delete_archivo(con, archivo_id):
    query = text("""DELETE FROM public.archivo WHERE archivo_id=:archivo_id RETURNING pista_son_id""")
    pista_son_id = con.execute(query, archivo_id=archivo_id).first()
    if pista_son_id is not None:
        path = app.config['UPLOAD_FOLDER'] + '/audio/' + str(pista_son_id[0]) + '/' + str(archivo_id)
        rmtree(path)


def upsert_pista_wrapper(fun, con, form, file, pista_id=None):
    trans = con.begin()
    try:
        if pista_id is None:
            pista_id = str(fun(con, form, session['id']))
        else:
            fun(con, form, session['id'], pista_id)
        if file is not None:
            upload_audio(con, pista_id, file)
        trans.commit()
        init_session(con, session['email'])
        return 'La actualización se ha realizado correctamente.', "success"
    except Exception as ex:
        trans.rollback()
        if app.config['DEBUG']:
            raise   # Only for development
        return 'Ocurrió un error; ' + str(ex), "danger"


    #########################
    # Views for registering #
    #########################

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
    result = query_perfil(con, session['id'], 'EDITOR')
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

    ##################################
    # Views for adding participantes #
    ##################################


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


@user_blueprint.route('/poner/persona/<int:obra_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_author
def poner_persona(obra_id):
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
    return render_template('poner/persona.html', form=form)


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


@user_blueprint.route('/retirar/persona/<int:obra_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_author
def retirar_persona(obra_id):
    con = engine.connect()
    delete_wrapper(delete_persona, con, obra_id, session['id'])
    con.close()
    return redirect(url_for('user.perfil', _anchor='tab_pista'))


@user_blueprint.route('/retirar/grupo/<int:obra_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_author
def retirar_grupo(obra_id):
    con = engine.connect()
    delete_wrapper(delete_grupo, con, obra_id, session['id'])
    con.close()
    return redirect(url_for('user.perfil', _anchor='tab_pista'))


    ############################################
    # Views for adding composicions and tracks #
    ############################################

@user_blueprint.route('/poner/composicion/<int:obra_id>/', methods=['GET', 'POST'])
@user_blueprint.route('/poner/composicion', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_author
def poner_composicion(obra_id=None):
    form = AddCompForm(request.form)
    con = engine.connect()
    if request.method == 'GET':
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
    return render_template('poner/composicion.html', form=form)


@user_blueprint.route('/poner/pista/<int:obra_id>/', methods=['GET', 'POST'])
@user_blueprint.route('/poner/pista', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_author
def poner_pista(obra_id=None):
    result = {}
    form = AddTrackForm(request.form)
    con = engine.connect()
    if request.method == 'GET':
        populate_pista(con, form, obra_id)
    add_pista_choices(con, form)
    result['archivos'] = query_archivos(con, obra_id)
    result['editor'] = True
    if obra_id is not None:
        result['obra_id'] = obra_id
    con.close()
    if request.method == 'POST' and form.validate():
        validated, file = validate_audio_file()
        con = engine.connect()
        if obra_id is None:
            # When inserting for the first time there must be a file
            if not validated:
                return jsonify(success="danger", msg=file)
            msg, success = upsert_pista_wrapper(insert_pista, con, form, file)
        else:
            if not validated:
                # On update a file need not be uploaded
                flash(file, 'warning')
                msg, success = upsert_pista_wrapper(update_pista, con, form, file=None, pista_id=obra_id)
            else:
                msg, success = upsert_pista_wrapper(update_pista, con, form, file, obra_id)
        con.close()
        if success:
            return jsonify(success=success, msg=msg)
        else:
            return jsonify(success=success, msg=msg)
    return render_template('poner/pista.html', form=form, result=result)


@user_blueprint.route('/retirar/comp/<int:obra_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_author
def retirar_comp(obra_id):
    con = engine.connect()
    delete_wrapper(delete_comp, con, obra_id, session['id'])
    con.close()
    return redirect(url_for('user.perfil', _anchor='tab_pista'))


@user_blueprint.route('/retirar/pista/<int:obra_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_author
def retirar_pista(obra_id):
    con = engine.connect()
    delete_wrapper(delete_pista, con, obra_id, session['id'])
    con.close()
    return redirect(url_for('user.perfil', _anchor='tab_pista'))


@user_blueprint.route('/retirar/archivo/<int:obra_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
def retirar_archivo(obra_id):
    con = engine.connect()
    delete_wrapper(delete_archivo, con, obra_id)
    con.close()
    return redirect(url_for('user.perfil', _anchor='tab_pista'))


    #####################################
    # Views for the mod and admin pages #
    #####################################

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


@user_blueprint.route('/estado/<obra>/<estado>/<int:obra_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_mod
def estado(obra, estado, obra_id):
    estados = ['DEPOSITAR', 'RECHAZADO', 'PENDIENTE', 'PUBLICADO']
    estado_upper = estado.upper()
    if estado_upper not in estados:
        abort(404)
    obras = ['comp', 'pista', 'pers', 'grupo']
    if obra not in obras:
        abort(404)
    con = engine.connect()
    try:
        if 'comp' in obra:
            estado_comp(con, obra_id, estado_upper, session['id'])
        elif 'pista' in obra:
            estado_pista(con, obra_id, estado_upper, session['id'])
        elif 'pers' in obra:
            estado_pers(con, obra_id, estado_upper, session['id'])
        elif 'grupo' in obra:
            estado_grupo(con, obra_id, estado_upper, session['id'])
    except Exception as ex:
        if app.config['DEBUG']:
            raise  # Only for development
        flash('Ocurrió un error;' + str(ex), 'danger')
    con.close()
    return '', 204


@user_blueprint.route('/permiso/<int:usuario_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_admin
def permiso(usuario_id):
    con = engine.connect()
    json = request.get_json()
    permiso = json['permiso'].upper()
    update_permiso(con, usuario_id, permiso)
    con.close()
    return '', 204


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
    return '', 204


    #######################################
    # Views for varios tab in perfil.html #
    #######################################

@user_blueprint.route('/poner/serie', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
def poner_serie():
    form = SerieForm(request.form)
    con = engine.connect()
    form.delete_serie.choices = populate_serie_form(con)
    con.close()
    if request.method == 'POST' and form.validate():
        con = engine.connect()
        insert_wrapper(insert_serie, con, form)
        con.close()
        return redirect(url_for('user.perfil', _anchor='tab_varios'))
    return render_template('poner/serie.html', form=form)


@user_blueprint.route('/poner/genero', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
def poner_genero():
    form = GenMusForm(request.form)
    con = engine.connect()
    form.delete_gen_mus.choices = populate_gen_mus_form(con)
    con.close()
    if request.method == 'POST' and form.validate():
        con = engine.connect()
        insert_wrapper(insert_genero, con, form)
        con.close()
        return redirect(url_for('user.perfil', _anchor='tab_varios'))
    return render_template('poner/genero.html', form=form)


@user_blueprint.route('/poner/idioma', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
def poner_idioma():
    form = IdiomaForm(request.form)
    con = engine.connect()
    form.delete_idioma.choices = populate_idiomas_form(con)
    con.close()
    if request.method == 'POST' and form.validate():
        con = engine.connect()
        insert_wrapper(insert_idioma, con, form)
        con.close()
        return redirect(url_for('user.perfil', _anchor='tab_varios'))
    return render_template('poner/idioma.html', form=form)


@user_blueprint.route('/poner/tema', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
def poner_tema():
    form = TemaForm(request.form)
    con = engine.connect()
    form.delete_tema.choices = populate_temas_form(con)
    con.close()
    if request.method == 'POST' and form.validate():
        con = engine.connect()
        insert_wrapper(insert_tema, con, form)
        con.close()
        return redirect(url_for('user.perfil', _anchor='tab_varios'))
    return render_template('poner/tema.html', form=form)


@user_blueprint.route('/poner/album', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
def poner_album():
    form = AlbumForm(request.form)
    con = engine.connect()
    form.delete_album.choices = populate_album_form(con)
    form.serie_id.choices = populate_serie_form(con)
    con.close()
    if request.method == 'POST' and form.validate():
        validated, file = validate_image_file()
        print(file)
        con = engine.connect()
        trans = con.begin()
        try:
            if validated:
                album_id = insert_album(con, form, file.filename)
                upload_album_image(file, album_id)
            else:
                insert_album(con, form, None)
                flash(file, 'warning')
            trans.commit()
            flash('La actualización se ha realizado correctamente.', 'success')
        except Exception as ex:
            trans.rollback()
            if app.config['DEBUG']:
                raise  # Only for development
            flash('Ocurrió un error; ' + str(ex), 'danger')
        con.close()
        return redirect(url_for('user.perfil', _anchor='tab_varios'))
    return render_template('poner/album.html', form=form)


@user_blueprint.route('/poner/instrumento', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
def poner_instrumento():
    form = InstrForm(request.form)
    con = engine.connect()
    form.familia_instr_id.choices = populate_inst_fam(con)
    form.delete_inst.choices = populate_instrumento_form(con)
    con.close()
    if request.method == 'POST' and form.validate():
        con = engine.connect()
        insert_wrapper(insert_inst, con, form)
        con.close()
        return redirect(url_for('user.perfil', _anchor='tab_varios'))
    return render_template('poner/instrumento.html', form=form)


@user_blueprint.route('/retirar/serie/<int:obra_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_mod
def retirar_serie(obra_id):
    con = engine.connect()
    delete_wrapper(delete_serie, con, obra_id)
    con.close()
    return redirect(url_for('user.perfil', _anchor='tab_pista'))


@user_blueprint.route('/retirar/inst/<int:obra_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_mod
def retirar_inst(obra_id):
    if obra_id == 1 or obra_id == 2:
        # cannot remove 'Ninguno' or 'voz' instruments
        flash('No se puede eliminar esta información', 'danger')
        return redirect(url_for('user.poner_instrumento'))
    else:
        con = engine.connect()
        delete_wrapper(delete_inst, con, obra_id)
        con.close()
    return redirect(url_for('user.perfil', _anchor='tab_pista'))


@user_blueprint.route('/retirar/tema/<int:obra_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_mod
def retirar_tema(obra_id):
    con = engine.connect()
    delete_wrapper(delete_tema, con, obra_id)
    con.close()
    return redirect(url_for('user.perfil', _anchor='tab_pista'))


@user_blueprint.route('/retirar/idioma/<int:obra_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_mod
def retirar_idioma(obra_id):
    con = engine.connect()
    delete_wrapper(delete_idioma, con, obra_id)
    con.close()
    return redirect(url_for('user.perfil', _anchor='tab_pista'))


@user_blueprint.route('/retirar/genero/<int:obra_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_mod
def retirar_genero(obra_id):
    con = engine.connect()
    delete_wrapper(delete_genero, con, obra_id)
    con.close()
    return redirect(url_for('user.perfil', _anchor='tab_pista'))


@user_blueprint.route('/retirar/album/<int:obra_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_mod
def retirar_album(obra_id):
    con = engine.connect()
    try:
        path = app.config['UPLOAD_FOLDER'] + '/images/albums/' + str(obra_id)
        rmtree(path)
        delete_album(con, obra_id)
        flash('la eliminación se ha realizado correctamente.', 'success')
    except Exception as ex:
        if app.config['DEBUG']:
            raise  # Only for development
        flash('Ocurrió un error;' + str(ex), 'danger')
    con.close()
    return redirect(url_for('user.perfil', _anchor='tab_pista'))

