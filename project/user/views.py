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

from project.user.models import query_ags, query_pers_ag, query_pers, populate_info, update_info, \
    insert_part, populate_poner_ag, populate_poner_pers, update_poner_ag, update_poner_pers, delete_part, \
    init_comps, init_pistas, init_pers, init_ags, insert_comp, query_comps, insert_pista, query_pista, \
    populate_ags_form, populate_pais_form, populate_genero_form, populate_tipo_ags_form, \
    populate_part_id_form, populate_rol_comp_form, populate_idiomas_form, populate_temas_form, populate_comps_form, \
    populate_instrumento_form, populate_rol_pista_form, populate_gen_mus_form, populate_comp, \
    populate_comps_pista_form, populate_medio_form, populate_serie_form, populate_pista, delete_comp, \
    delete_pista, insert_inst, insert_serie, delete_inst, delete_serie, populate_inst_fam


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


def add_pista_choices(con, form):
    for sub_form in form.gen_mus_form:
        sub_form.gen_mus_id.choices = populate_gen_mus_form(con)
    for sub_form in form.interp_form:
        sub_form.part_id.choices = populate_part_id_form(con)
        sub_form.rol_pista_son.choices = populate_rol_pista_form(con)
        sub_form.instrumento_id.choices = populate_instrumento_form(con)
    form.medio.choices = populate_medio_form(con)
    form.serie_id.choices = populate_serie_form(con)
    form.comp_id.choices = populate_comps_pista_form(con)
    form.pais.choices = populate_pais_form(con)


def add_comp_choices(con, form):
    for sub_form in form.part_id_form:
        sub_form.part_id.choices = populate_part_id_form(con)
        sub_form.rol_composicion.choices = populate_rol_comp_form(con)
    for sub_form in form.idioma_form:
        sub_form.idioma_id.choices = populate_idiomas_form(con)
    for sub_form in form.tema_form:
        sub_form.tema_id.choices = populate_temas_form(con)
    form.comp_id.choices = populate_comps_form(con)


def add_part_choices(con, form):
    for sub_form in form.org_form:
        sub_form.agregar_id.choices = populate_ags_form(con)
    form.tipo_agregar.choices = populate_tipo_ags_form(con)
    form.genero.choices = populate_genero_form(con)
    form.pais.choices = populate_pais_form(con)
    form.pais_muer.choices = populate_pais_form(con)


# The view start here


@user_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data.strip(' ')
        nom_usario = form.nom_usario.data.strip(' ')
        contrasena = bcrypt.using(rounds=13).hash(str(form.contrasena.data))
        con = engine.connect()
        if form.user_type.data == 'persona':
            user_query = text("""INSERT INTO public.us_pers (email, nom_usario, contrasena) VALUES 
                          (:email, :nom_usario, :contrasena);""")
            con.execute(user_query, email=email, nom_usario=nom_usario, contrasena=contrasena)
        else:
            user_query = text("""INSERT INTO public.us_ag (email, nom_usario, contrasena) VALUES 
                          (:email, :nom_usario, :contrasena);""")
            con.execute(user_query, email=email, nom_usario=nom_usario, contrasena=contrasena)
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
    for sub_form in form.org_form:
        sub_form.agregar_id.choices = populate_ags_form(con)
    form.tipo_agregar.choices = populate_tipo_ags_form(con)
    form.genero.choices = populate_genero_form(con)
    form.pais.choices = populate_pais_form(con)
    con.close()
    if request.method == 'POST' and form.validate():
        con = engine.connect()
        upsert_wrapper(update_info, con, form)
        return redirect(url_for('user.profile'))
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
        confirm_user = text("""UPDATE public.usario
                                  SET confirmado=TRUE
                                    , fecha_confirmado=now() 
                                  WHERE usario_id=:id""")
        con.execute(confirm_user, id=session['id'])
        session['confirmed'] = True
        flash('Has confirmado tu cuenta. ¡Gracias!', 'success')
    con.close()
    return redirect(url_for('user.profile'))


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
            reset_pass = text("""UPDATE public.usario SET contrasena=:password 
                                  WHERE usario_id=:id""")
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
        return redirect(url_for('user.profile'))
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
        return redirect(url_for('user.profile'))
    return render_template('user/login.html', form=form)


@user_blueprint.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('Usted fue desconectado.', 'success')
    return redirect(url_for('user.login'))


@user_blueprint.route('/profile', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
def profile():
    con = engine.connect()
    if session['is_person']:
        user = current_pers(con, session['email'])
    else:
        user = current_ag(con, session['email'])
    pers_ag = query_pers_ag(con, session['id'])
    pers = query_pers(con, session['id'])
    ags = query_ags(con, session['id'])
    comps = query_comps(con, session['id'])
    pista = query_pista(con, session['id'])
    con.close()
    password_form = ChangePasswordForm(request.form)
    if request.method == 'POST' and password_form.validate():
        if user and bcrypt.verify(password_form.old_password.data, user.contrasena):
            con = engine.connect()
            password = bcrypt.using(rounds=13).hash(str(password_form.new_password.data))
            reset_pass = text("""UPDATE public.usario SET contrasena=:password 
                                  WHERE usario_id=:id""")
            con.execute(reset_pass, id=user.part_id, password=password)
            con.close()
            flash('Contraseña cambiada correctamente.', 'success')
        else:
            flash('El cambio de contraseña no tuvo éxito.', 'danger')
        return redirect(url_for('user.profile', _anchor='tab_contrasena'))
    return render_template('user/profile.html', user=user
                                              , pers_ag=pers_ag
                                              , pers=pers
                                              , ags=ags
                                              , comps=comps
                                              , pista=pista
                                              , password_form=password_form)


@user_blueprint.route('/poner_part', methods=['GET', 'POST'])
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
        return redirect(url_for('user.profile', _anchor='tab_part'))
    return render_template('user/poner/poner_part.html', form=form)


@user_blueprint.route('/poner_pers/<int:part_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_author
def poner_pers(part_id):
    form = UpdateEntityForm(request.form)
    con = engine.connect()
    if request.method == 'GET':
        populate_poner_pers(con, form, part_id)
    add_part_choices(con, form)
    con.close()
    if request.method == 'POST' and form.validate():
        con = engine.connect()
        upsert_wrapper(update_poner_pers, con, form, part_id)
        con.close()
        return redirect(url_for('user.profile', _anchor='tab_part'))
    return render_template('user/poner/poner_pers.html', form=form)


@user_blueprint.route('/poner_ag/<int:part_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_author
def poner_ag(part_id):
    form = UpdateEntityForm(request.form)
    con = engine.connect()
    if request.method == 'GET':
        populate_poner_ag(con, form, part_id)
    add_part_choices(con, form)
    con.close()
    if request.method == 'POST' and form.validate():
        con = engine.connect()
        upsert_wrapper(update_poner_ag, con, form, part_id)
        return redirect(url_for('user.profile', _anchor='tab_part'))
    return render_template('user/poner/poner_ag.html', form=form)


@user_blueprint.route('/remove_part/<int:part_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_author
def remove_part(part_id):
    con = engine.connect()
    delete_wrapper(delete_part, con, part_id)
    con.close()
    return redirect(url_for('user.profile', _anchor='tab_part'))


@user_blueprint.route('/remove_comp/<int:comp_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_author
def remove_comp(comp_id):
    con = engine.connect()
    delete_wrapper(delete_comp, con, comp_id)
    con.close()
    return redirect(url_for('user.profile', _anchor='tab_pista'))


@user_blueprint.route('/remove_pista/<int:pista_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_author
def remove_pista(pista_id):
    con = engine.connect()
    delete_wrapper(delete_pista, con, pista_id)
    con.close()
    return redirect(url_for('user.profile', _anchor='tab_pista'))



@user_blueprint.route('/poner_comp', methods=['GET', 'POST'])
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
        return redirect(url_for('user.profile', _anchor='tab_pista'))
    return render_template('user/poner/poner_comp.html', form=form)


@user_blueprint.route('/poner_pista', methods=['GET', 'POST'])
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
        return redirect(url_for('user.profile', _anchor='tab_pista'))
    return render_template('user/poner/poner_pista.html', form=form)


@user_blueprint.route('/poner_comp/<int:comp_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_author
def update_comp(comp_id):
    form = AddCompForm(request.form)
    con = engine.connect()
    if request.method == 'GET':
        populate_comp(con, form, comp_id)
    add_comp_choices(con, form)
    form.comp_id.choices = populate_comps_form(con)
    con.close()
    if request.method == 'POST' and form.validate():
        con = engine.connect()
        upsert_wrapper(update_comp, con, form, comp_id)
        con.close()
        return redirect(url_for('user.profile', _anchor='tab_pista'))
    return render_template('user/poner/poner_comp.html', form=form)


@user_blueprint.route('/poner_pista/<int:pista_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
@is_author
def update_pista(pista_id):
    form = AddTrackForm(request.form)
    con = engine.connect()
    if request.method == 'GET':
        populate_pista(con, form, pista_id)
    add_pista_choices(con, form)
    con.close()
    if request.method == 'POST' and form.validate():
        con = engine.connect()
        trans = con.begin()
        try:
            update_pista(con, form, pista_id, session['id'])
            trans.commit()
            flash('La actualización se ha realizado correctamente.', 'success')
            init_session(con, session['email'])
        except:
            trans.rollback()
            if app.config['DEBUG']:
                raise  # Only for development
            flash('Ocurrió un error.', 'danger')
        con.close()
        return redirect(url_for('user.profile', _anchor='tab_pista'))
    return render_template('user/poner/poner_pista.html', form=form)


@user_blueprint.route('/poner_serie', methods=['GET', 'POST'])
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
        return redirect(url_for('user.profile', _anchor='tab_pista'))
    return render_template('user/poner/poner_serie.html', form=form)


@user_blueprint.route('/poner_inst', methods=['GET', 'POST'])
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
        return redirect(url_for('user.profile', _anchor='tab_pista'))
    return render_template('user/poner/poner_inst.html', form=form)


@user_blueprint.route('/remove_serie/<int:serie_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
def remove_serie(serie_id):
    con = engine.connect()
    delete_wrapper(delete_serie, con, serie_id)
    con.close()
    return redirect(url_for('user.profile', _anchor='tab_pista'))


@user_blueprint.route('/remove_inst/<int:inst_id>/', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
def remove_inst(inst_id):
    con = engine.connect()
    delete_wrapper(delete_inst, con, inst_id)
    con.close()
    return redirect(url_for('user.profile', _anchor='tab_pista'))
