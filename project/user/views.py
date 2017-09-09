# project/user/views.py
# coding=utf-8

#################
#### imports ####
#################

from flask import render_template, Blueprint, url_for, \
    redirect, flash, request, session, abort
from sqlalchemy import text
from project.token import generate_confirmation_token, confirm_token, ts
from project import engine
from passlib.hash import bcrypt
from .forms import LoginForm, RegisterForm, \
    ChangePasswordForm, EmailForm, PasswordForm, \
    InfoForm, current_user, AddEntityForm, AddTrackForm, OrgForm
from project.decorators import check_confirmed, is_admin, is_logged_in, is_mod
from project.util import current_user, current_org, current_pers, parse_fecha, send_email

################
#### config ####
################

user_blueprint = Blueprint('user', __name__,)


################
#### routes ####
################


def init_session(con, email):
    user = current_org(con, email)
    if user is None:
        user = current_pers(con, email)
        session['is_person'] = True
    else:
        session['is_person'] =False
    session['logged_in'] = True
    session['id'] = int(user.part_id)
    session['confirmed'] = user.confirmado
    if user.permiso == 'ADMIN':
        session['permission'] = 'ADMIN'
    elif user.permiso == 'MOD':
        session['permission'] = 'MOD'
    else:
        session['permission'] = 'EDITOR'
    session['email'] = user.email

    # get a list of composicions by this user
    comps_query = text("""SELECT composicion_id 
                            FROM limbo.composicion_limbo
                            WHERE cargador_id=:id 
                              AND estado='PENDIENTE'
                              OR estado='PUBLICADO'""")
    comps_result = con.execute(comps_query, id=session['id'])
    session['comps'] = [comp for comp in comps_result]

    # list of artists added
    part_query = text("""SELECT part_id FROM limbo.participante_limbo
                              WHERE cargador_id=:id
                              AND estado='PENDIENTE'
                              OR estado='PUBLICADO'""")
    part_result = con.execute(part_query, id=session['id'])
    session['part'] = [pers for pers in part_result]

    # list of pista_son added
    pista_query = text("""SELECT pista_son_id FROM limbo.pista_son_limbo
                              WHERE cargador_id=:id
                              AND estado='PENDIENTE'
                              OR estado='PUBLICADO'""")
    pista_result = con.execute(pista_query, id=session['id'])
    session['pista'] = [pista for pista in pista_result]



@user_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data.strip(' ')
        nom_usario = form.nom_usario.data.strip(' ')
        contrasena = bcrypt.using(rounds=13).hash(str(form.contrasena.data))
        con = engine.connect()
        if int(form.user_type.data) == 0:
            user_query = text("""INSERT INTO public.part_us_pers (email, nom_usario, contrasena, seudonimo) VALUES 
                          (:email, :nom_usario, :contrasena, :nom_usario);""")
            con.execute(user_query, email=email, nom_usario=nom_usario, contrasena=contrasena)
        else:
            user_query = text("""INSERT INTO public.part_us_ag (email, nom_usario, contrasena) VALUES 
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
    if request.method == 'GET':
        # prepopulate
        con = engine.connect()
        if session['is_person']:
            user = current_pers(con, session['email'])
            pers_org_query = text("""SELECT pa.agregar_id
                                          , public.get_fecha(pa.fecha_comienzo) fecha_comienzo
                                          , public.get_fecha(pa.fecha_finale) fecha_finale
                                          , pa.titulo
                                          FROM public.persona_agregar pa
                                          WHERE pa.persona_id=:id""")
            pers_org_result = con.execute(pers_org_query, id=session['id'])

            for res in pers_org_result:
                org_form = OrgForm()
                org_form.agregar_id = str(res.agregar_id)
                org_form.titulo = res.titulo
                org_form.fecha_comienzo = res.fecha_comienzo
                org_form.fecha_finale = res.fecha_finale
                
                form.org_form.append_entry(org_form)

            form.nom_part.data = user.nom_part
            form.nom_segundo.data = user.nom_segundo
            form.seudonimo.data = user.seudonimo
            form.fecha_comienzo.data = user.fecha_comienzo
            form.nom_paterno.data = user.nom_paterno
            form.nom_materno.data = user.nom_materno
            form.genero.data = user.genero
        else:
            user = current_org(con, session['email'])
            form.nom_part_ag.data = user.nom_part
            form.fecha_comienzo_ag.data = user.fecha_comienzo
            form.tipo_agregar.data = user.tipo_agregar
        form.coment_part.data = user.coment_part
        form.sitio_web.data = user.sitio_web
        form.direccion.data = user.direccion
        form.telefono.data = user.telefono
        form.ciudad.data = user.ciudad
        form.nom_subdivision.data = user.nom_subdivision
        form.tipo_subdivision.data = user.tipo_subdivision
        form.pais.data = user.pais
        con.close()
    if request.method == 'POST' and form.validate():
        con = engine.connect()
        trans = con.begin()
        try:
            if session['is_person']:
                user_query = text("""UPDATE public.part_pers SET nom_part=strip(:nom_part)
                                                         , nom_segundo=strip(:nom_segundo)
                                                         , seudonimo=strip(:seudonimo)
                                                         , nom_materno=strip(:nom_materno)
                                                         , nom_paterno=strip(:nom_paterno)
                                                         , ciudad=strip(:ciudad)
                                                         , nom_subdivision=strip(:nom_subdivision)
                                                         , tipo_subdivision=strip(:tipo_subdivision)
                                                         , pais=strip(:pais)
                                                         , fecha_comienzo_insert=:fecha_comienzo
                                                         , sitio_web=strip(:sitio_web)
                                                         , direccion=strip(:direccion)
                                                         , telefono=strip(:telefono)
                                                         , genero=strip(:genero)
                                                         , coment_part=strip(:coment_part)
                                                         , actualizador_id=:id
                                                         WHERE pp_id=:id;""")
                con.execute(user_query, nom_part=form.nom_part.data
                                    , nom_segundo=form.nom_segundo.data
                                    , seudonimo=form.seudonimo.data
                                    , nom_materno=form.nom_materno.data
                                    , nom_paterno=form.nom_paterno.data
                                    , ciudad=form.ciudad.data
                                    , nom_subdivision=form.nom_subdivision.data
                                    , tipo_subdivision=form.tipo_subdivision.data
                                    , pais=form.pais.data
                                    , fecha_comienzo=parse_fecha(form.fecha_comienzo.data)
                                    , sitio_web=form.sitio_web.data
                                    , direccion=form.direccion.data
                                    , telefono=form.telefono.data
                                    , genero=form.genero.data
                                    , coment_part=form.coment_part.data
                                    , id=session['id'])
                pers_ag_delete = text("""DELETE FROM public.persona_agregar WHERE persona_id=:id""")
                con.execute(pers_ag_delete, id=session['id'])
                for entry in form.org_form.entries:
                    pers_ag_insert = text("""INSERT INTO public.persona_agregar VALUES (:id
                                              , :agregar_id, :fecha_comienzo
                                              , :fecha_finale, strip(:titulo), :id)""")
                    con.execute(pers_ag_insert, id=session['id']
                                      , agregar_id=entry.data['agregar_id']
                                      , fecha_comienzo=parse_fecha(entry.data['fecha_comienzo'])
                                      , fecha_finale=parse_fecha(entry.data['fecha_finale'])
                                      , titulo=entry.data['titulo'])

            else:
                user_query = text("""UPDATE public.part_ag SET nom_part=strip(:nom_part_ag)
                                                         , ciudad=strip(:ciudad)
                                                         , nom_subdivision=strip(:nom_sudivision)
                                                         , tipo_subdivision=strip(:tipo_sudivision)
                                                         , pais=strip(:pais)
                                                         , fecha_comienzo_insert=:fecha_comienzo_ag
                                                         , sitio_web=strip(:sitio_web)
                                                         , direccion=strip(:direccion)
                                                         , telefono=strip(:telefono)
                                                         , coment_part=strip(:coment_part)
                                                         , tipo_agregar=strip(:tipo_agregar)
                                                         , actualizador_id=:id
                                                         WHERE pa_id=:id;""")
                con.execute(user_query, nom_part_ag=form.nom_part_ag.data
                                    , ciudad=form.ciudad.data
                                    , nom_subdivision=form.nom_subdivision.data
                                    , tipo_subdivision=form.tipo_subdivision.data
                                    , pais=form.pais.data
                                    , date_formed=parse_fecha(form.fecha_comienzo_ag.data)
                                    , sitio_web=form.sitio_web.data
                                    , direccion=form.direccion.data
                                    , telefono=form.telefono.data
                                    , coment_part=form.coment_part.data
                                    , tipo_agregar=form.tipo_agregar.data
                                    , id=session['id'])
            trans.commit()
            flash('Añadir fue un éxito', 'success')
        except:
            trans.rollback()
            raise
            flash('Ocurrió un error.', 'danger')
        con.close()
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
                                  WHERE part_id=:id""")
        con.execute(confirm_user, id=session['id'])
        session['confirmed'] = True
        flash('Has confirmado tu cuenta. ¡Gracias!', 'success')
    con.close()
    return redirect(url_for('user.profile'))


@user_blueprint.route('/reset', methods=["GET", "POST"])
def reset():
    form = EmailForm()
    if form.validate_on_submit():
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
                                  WHERE part_id:id""")
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
        return redirect(url_for('user.profile', _anchor='tab_home'))
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
        user = current_org(con, session['email'])
    pers_ag_query = text("""SELECT p.nom_part
                                 , public.get_fecha(pa.fecha_comienzo) fecha_comienzo
                                 , public.get_fecha(pa.fecha_finale)  fecha_finale
                                 , pa.titulo
                                FROM public.persona_agregar pa
                                JOIN public.participante p
                                  ON pa.agregar_id = p.part_id
                                  WHERE pa.persona_id=:id""")
    pers_ag_result = con.execute(pers_ag_query, id=session['id'])
    con.close()
    track_form = AddTrackForm(request.form)
    password_form = ChangePasswordForm(request.form)
    if request.method == 'POST' and password_form.validate():
        if user and bcrypt.verify(password_form.old_password.data, user.contrasena):
            con = engine.connect()
            password = bcrypt.using(rounds=13).hash(str(password_form.new_password.data))
            reset_pass = text("""UPDATE public.usario SET contrasena=:password 
                                  WHERE part_id=:id""")
            con.execute(reset_pass, id=user.part_id, password=password)
            con.close()
            flash('Contraseña cambiada correctamente.', 'success')
        else:
            flash('El cambio de contraseña no tuvo éxito.', 'danger')
        return redirect(url_for('user.profile', _anchor='tab_contrasena'))
    return render_template('user/profile.html', user=user
                                              , pers_ag=pers_ag_result
                                              , password_form=password_form
                                              , track_form=track_form)


@user_blueprint.route('/poner_part/<int:part_id>/', methods=['GET', 'POST'])
@user_blueprint.route('/poner_part', methods=['GET', 'POST'])
@is_logged_in
@check_confirmed
def poner_part(part_id=None):
    form = AddEntityForm(request.form)
    if request.method == 'POST' and form.validate():
        con = engine.connect()
        trans = con.begin()
        try:
            if int(form.user_type.data) == 0:
                user_query= text("""INSERT INTO public.part_pers(nom_part
                                                                   , nom_segundo
                                                                   , seudonimo
                                                                   , nom_paterno
                                                                   , nom_materno
                                                                   , ciudad
                                                                   , nom_subdivision
                                                                   , tipo_subdivision
                                                                   , pais
                                                                   , ciudad_muer
                                                                   , nom_subdivision_muer
                                                                   , tipo_subdivision_muer
                                                                   , pais_muer
                                                                   , fecha_comienzo_insert
                                                                   , fecha_finale_insert
                                                                   , sitio_web
                                                                   , direccion
                                                                   , telefono
                                                                   , email
                                                                   , genero
                                                                   , coment_participante)
                                                                 VALUES (strip(:nom_part)
                                                                       , strip(:nom_segundo)
                                                                       , strip(:seudonimo)
                                                                       , strip(:nom_paterno)
                                                                       , strip(:nom_materno)
                                                                       , strip(:ciudad)
                                                                       , strip(:nom_subdivision)
                                                                       , strip(:tipo_subdivision)
                                                                       , strip(:pais)
                                                                       , strip(:ciudad_muer)
                                                                       , strip(:nom_subdivision_muer)
                                                                       , strip(:tipo_subdivision_muer)
                                                                       , strip(:pais_muer)
                                                                       , :fecha_comienzo_insert
                                                                       , :fecha_finale_insert
                                                                       , strip(:sitio_web)
                                                                       , strip(:direccion)
                                                                       , strip(:telefono)
                                                                       , strip(:email)
                                                                       , strip(:genero)
                                                                       , strip(:coment_participante))""")
                con.execute(user_query, nom_part=form.nom_part.data
                                        , nom_segundo=form.nom_segundo.data
                                        , seudonimo=form.seudonimo.data
                                        , nom_materno=form.nom_materno.data
                                        , nom_paterno=form.nom_paterno.data
                                        , ciudad=form.ciudad.data
                                        , nom_subdivision=form.nom_subdivision.data
                                        , tipo_subdivision=form.tipo_subdivision.data
                                        , pais=form.pais.data
                                        , ciudad_muer=form.ciudad.data
                                        , nom_subdivision_muer=form.nom_subdivision_muer.data
                                        , tipo_subdivision_muer=form.tipo_subdivision_muer.data
                                        , pais_muer=form.pais_muer.data
                                        , fecha_comienzo=parse_fecha(form.fecha_comienzo.data)
                                        , fecha_finale=parse_fecha(form.fecha_finale.data)
                                        , sitio_web=form.sitio_web.data
                                        , direccion=form.direccion.data
                                        , telefono=form.telefono.data
                                        , genero=form.genero.data
                                        , coment_part=form.coment_part.data
                                        , cargador_id=session['id'])
                pers_ag_delete = text("""DELETE FROM public.persona_agregar WHERE persona_id=:id""")
                con.execute(pers_ag_delete, id=session['id'])
                for entry in form.org_form.entries:
                        pers_ag_insert = text("""INSERT INTO public.persona_agregar VALUES (:id
                                                  , :agregar_id, :fecha_comienzo
                                                  , :fecha_finale, strip(:titulo), :id)""")
                        con.execute(pers_ag_insert, id=session['id']
                                          , agregar_id=entry.data['agregar_id']
                                          , fecha_comienzo=parse_fecha(entry.data['fecha_comienzo'])
                                          , fecha_finale=parse_fecha(entry.data['fecha_finale'])
                                          , titulo=entry.data['titulo'])
            else:
                user_query = text("""INSERT INTO public.part_ag(nom_part
                                                                   , ciudad
                                                                   , nom_subdivision
                                                                   , tipo_subdivision
                                                                   , pais
                                                                   , fecha_comienzo_insert
                                                                   , fecha_finale_insert
                                                                   , sitio_web
                                                                   , direccion
                                                                   , telefono
                                                                   , email
                                                                   , tipo_agregar
                                                                   , coment_participante)
                                                                 VALUES (strip(:nom_part)
                                                                       , strip(:ciudad)
                                                                       , strip(:nom_subdivision)
                                                                       , strip(:tipo_subdivision)
                                                                       , strip(:pais)
                                                                       , :fecha_comienzo_insert
                                                                       , :fecha_finale_insert
                                                                       , strip(:sitio_web)
                                                                       , strip(:direccion)
                                                                       , strip(:telefono)
                                                                       , strip(:email)
                                                                       , strip(:tipo_agregar)
                                                                       , strip(:coment_participante))""")
                con.execute(user_query, nom_part_ag=form.nom_part_ag.data
                                        , ciudad=form.ciudad.data
                                        , nom_subdivision=form.nom_subdivision.data
                                        , tipo_subdivision=form.tipo_subdivision.data
                                        , pais=form.pais.data
                                        , date_formed=parse_fecha(form.fecha_comienzo_ag.data)
                                        , sitio_web=form.sitio_web.data
                                        , direccion=form.direccion.data
                                        , telefono=form.telefono.data
                                        , coment_part=form.coment_part.data
                                        , tipo_agregar=form.tipo_agregar.data
                                        , id=session['id'])
            trans.commit()
            flash('Añadir fue un éxito.', 'success')
        except:
            trans.rollback()
            flash('Ocurrió un error.', 'danger')
        con.close()
        return redirect(url_for('user.profile', _anchor='tab_part'))
    return render_template('user/poner_part.html', form=form)

