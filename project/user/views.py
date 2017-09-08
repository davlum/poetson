# project/user/views.py


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


def init_session(user_result):
    session['logged_in'] = True
    session['id'] = int(user_result.part_id)
    session['confirmed'] = user_result.confirmado
    if user_result.permiso == 'ADMIN':
        session['permission'] = 'ADMIN'
    elif user_result.permiso == 'MOD':
        session['permission'] = 'MOD'
    else:
        session['permission'] = 'EDITOR'
    session['email'] = user_result.email
    con = engine.connect()
    session['is_person'] = (current_org(con, user_result.email) is None)
    con.close()


@user_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data.strip(' ')
        username = form.username.data.strip(' ')
        password = bcrypt.using(rounds=13).hash(str(form.password.data))
        con = engine.connect()
        if int(form.user_type.data) == 0:
            user_query = text("""INSERT INTO public.part_us_pers (email, nom_usario, contrasena, seudonimo) VALUES 
                          (:email, :username, :password, :username);""")
            con.execute(user_query, email=email, username=username, password=password)
        else:
            user_query = text("""INSERT INTO public.part_us_ag (email, nom_usario, contrasena) VALUES 
                          (:email, :name, :password);""")
            con.execute(user_query, email=email, name=username, password=password)
        user = current_user(con,  email)
        con.close()
        token = generate_confirmation_token(email)
        confirm_url = url_for('user.confirm_email', token=token, _external=True)
        html = render_template('user/activate.html', confirm_url=confirm_url)
        subject = "Por favor, confirma tu email"
        send_email(email, subject, html)

        init_session(user)

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
                                          , get_fecha(pa.fecha_comienzo) fecha_comienzo
                                          , get_fecha(pa.fecha_finale) fecha_finale
                                          , pa.titulo
                                          FROM public.persona_agregar pa
                                          WHERE pa.persona_id=:id""")
            pers_org_result = con.execute(pers_org_query, id=session['id'])

            for res in pers_org_result:
                org_form = OrgForm()
                org_form.nom_ag = str(res.agregar_id)
                org_form.title = res.titulo
                org_form.date_joined = res.fecha_comienzo
                org_form.date_left = res.fecha_finale
                
                form.org_form.append_entry(org_form)

            form.first_name.data = user.nom_part
            form.last_name.data = user.nom_segundo
            form.pseudonym.data = user.seudonimo
            form.dob.data = user.fecha_comienzo
            form.dad_name.data = user.nom_paterno
            form.mom_name.data = user.nom_materno
            form.gender.data = user.genero
        else:
            user = current_org(con, session['email'])
            form.org_name.data = user.nom_part
            form.date_formed.data = user.fecha_comienzo
            form.tipo_ag.data = user.tipo_agregar
        form.comment.data = user.coment_participante
        form.website.data = user.sitio_web
        form.address.data = user.direccion
        form.telephone.data = user.telefono
        form.city.data = user.ciudad
        form.subdiv.data = user.nom_subdivision
        form.subdiv_type.data = user.tipo_subdivision
        form.country.data = user.pais
        con.close()
    if request.method == 'POST' and form.validate():
        con = engine.connect()
        trans = con.begin()
        try:
            if session['is_person']:
                user_query = text("""UPDATE public.part_pers SET nom_part=strip(:first_name)
                                                         , nom_segundo=strip(:last_name)
                                                         , seudonimo=strip(:pseudonym)
                                                         , nom_materno=strip(:mom_name)
                                                         , nom_paterno=strip(:dad_name)
                                                         , ciudad=strip(:city)
                                                         , nom_subdivision=strip(:subdiv)
                                                         , tipo_subdivision=strip(:subdiv_type)
                                                         , pais=strip(:country)
                                                         , fecha_comienzo_insert=:dob
                                                         , fecha_finale_insert=:dod
                                                         , sitio_web=strip(:site)
                                                         , direccion=strip(:address)
                                                         , telefono=strip(:telephone)
                                                         , genero=strip(:gender)
                                                         , coment_participante=strip(:comment)
                                                         WHERE email=:email;""")
                con.execute(user_query, first_name=form.first_name.data
                                    , last_name=form.last_name.data
                                    , pseudonym=form.pseudonym.data
                                    , mom_name=form.mom_name.data
                                    , dad_name=form.dad_name.data
                                    , city=form.city.data
                                    , subdiv=form.subdiv.data
                                    , subdiv_type=form.subdiv_type.data
                                    , country=form.country.data
                                    , dob=parse_fecha(form.dob.data)
                                    , dod=parse_fecha(form.dod.data)
                                    , site=form.website.data
                                    , address=form.address.data
                                    , telephone=form.telephone.data
                                    , gender=form.gender.data
                                    , comment=form.comment.data
                                    , email=session['email'])
                pers_ag_delete = text("""DELETE FROM public.persona_agregar WHERE persona_id=:id""")
                con.execute(pers_ag_delete, id=session['id'])
                for entry in form.org_form.entries:
                    pers_ag_insert = text("""INSERT INTO public.persona_agregar VALUES (:id, 
                                              :ag_id, :start, :end, strip(:title), :id)""")
                    con.execute(pers_ag_insert, id=session['id']
                                      , ag_id=entry.data['nom_ag']
                                      , start=parse_fecha(entry.data['date_joined'])
                                      , end=parse_fecha(entry.data['date_left'])
                                      , title=entry.data['title'])

            else:
                user_query = text("""UPDATE public.part_ag SET nom_part=strip(:org_name)
                                                         , ciudad=strip(:city)
                                                         , nom_subdivision=strip(:subdiv)
                                                         , tipo_subdivision=strip(:subdiv_type)
                                                         , pais=strip(:country)
                                                         , fecha_comienzo_insert=:date_formed
                                                         , sitio_web=strip(:site)
                                                         , direccion=strip(:address)
                                                         , telefono=strip(:telephone)
                                                         , coment_participante=strip(:comment)
                                                         , tipo_agregar=strip(:tipo_ag)
                                                         WHERE email=:email;""")
                con.execute(user_query, org_name=form.org_name.data
                                    , city=form.city.data
                                    , subdiv=form.subdiv.data
                                    , subdiv_type=form.subdiv_type.data
                                    , country=form.country.data
                                    , date_formed=parse_fecha(form.date_formed.data)
                                    , site=form.website.data
                                    , address=form.address.data
                                    , telephone=form.telephone.data
                                    , comment=form.comment.data
                                    , tipo_ag=form.tipo_ag.data
                                    , email=session['email'])
            trans.commit()
            return redirect(url_for('user.unconfirmed'))
        except:
            trans.rollback()
        flash('Ocurrió un error.', 'danger')
        con.close()
        flash('El enlace de confirmación no es válido o ha caducado.', 'danger')
        return render_template('user/info.html', form=form)
    return render_template('user/info.html', form=form)


@user_blueprint.route('/confirm/<token>')
@is_logged_in
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('El enlace de confirmación no es válido o ha caducado.', 'danger')
    if session['confirmed']:
        flash('Cuenta ya confirmada. Por favor Iniciar sesión.', 'success')
    else:
        con = engine.connect()
        confirm_user = text("""UPDATE usario SET confirmado=TRUE, fecha_confirmado=now() 
                                  WHERE part_id=:id""")
        con.execute(confirm_user, id=session['id'])
        user = current_user(con,  session['email'])
        con.close()
        init_session(user)
        flash('Has confirmado tu cuenta. ¡Gracias!', 'success')
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

    if form.validate_on_submit():
        con = engine.connect()
        user = current_user(con,  email)
        if user and user.confirmado:
            password = bcrypt.using(rounds=13).hash(str(form.password.data))
            reset_pass = text("""UPDATE public.usario SET contrasena=:password 
                                  WHERE part_id:id""")
            con.execute(reset_pass, id=user.part_id, password=password)
            con.close()
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
        user = current_user(con, form.email.data)
        con.close()
        init_session(user)
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
    con.close()
    track_form = AddTrackForm(request.form)
    password_form = ChangePasswordForm(request.form)
    add_entity_form = AddEntityForm(request.form)
    if request.method == 'POST' and password_form.validate() and 'password_form' in request.form:
        con = engine.connect()
        user = current_user(con,  session['email'])
        if user and bcrypt.verify(password_form.old_password.data, user.contrasena):
            password = bcrypt.using(rounds=13).hash(str(password_form.new_password.data))
            reset_pass = text("""UPDATE usario SET contrasena=:password 
                                  WHERE part_id=:id""")
            con.execute(reset_pass, id=user.part_id, password=password)
            flash('Contraseña cambiada correctamente.', 'success')
        else:
            flash('El cambio de contraseña no tuvo éxito.', 'danger')
        con.close()
        return redirect(url_for('user.profile', _anchor='tab_change-pass'))
    if request.method == 'POST' and add_entity_form.validate() and 'add_entity_form' in request.form:
        return redirect(url_for('user.profile', _anchor='tab_add-entity'))
    return render_template('user/profile.html', user=user, password_form=password_form
                                                         , add_entity_form=add_entity_form
                                                         , track_form=track_form)


