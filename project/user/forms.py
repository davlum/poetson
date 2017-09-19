# project/user/forms.py
# coding=utf-8

from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, RadioField, \
    TextAreaField, SelectField, BooleanField, FileField, FieldList, FormField
from wtforms.validators import DataRequired, Email, Length, EqualTo, \
    InputRequired, Optional, URL, Regexp, ValidationError
from project import engine
from sqlalchemy import text
from passlib.hash import bcrypt
from project.util import current_user
from re import compile
from dateutil.parser import parse


# Custom validators
class Date(object):
    def __init__(self,  message=None, pat=None):
        if not pat:
            pat = compile('[(^\d{1,2}\/\d{1,2}\/\d{4}$)(^\d{4}$)(^\d{1,2}\/\d{4}$)]')
        self.pat = pat
        if not message:
            message = u'formato incorrecto'
        self.message = message

    def __call__(self, form, field):
        if self.pat.match(str(form.data).strip(' ')) is not None:
            try:
                parse(field.data)
            except ValueError:
                raise ValidationError(self.message)
        else:
            raise ValidationError(self.message)


class LessThanDate(object):
    def __init__(self, other_field_name, *args, **kwargs):
        self.other_field_name = other_field_name

    def __call__(self, form, field):
        other_field = form[self.other_field_name].data.strip()
        if other_field is not None and other_field != "":
            if other_field.split('/')[::-1] < field.data.split('/')[::-1]:
                raise ValidationError('Debe ser menos que "%s"' % self.other_field_name)


class GreaterThanDate(object):
    def __init__(self, other_field_name,  *args, **kwargs):
        self.other_field_name = other_field_name

    def __call__(self, form, field):
        other_field = form[self.other_field_name].data.strip()
        if field.data is not None and field.data != "":
            if other_field.split('/')[::-1] > field.data.split('/')[::-1]:
                raise ValidationError('Debe ser mayor que "%s"' % self.other_field_name)


class RequiredIf(DataRequired):
    """Validator which makes a field required if another field is set and has a truthy value.

    Sources:
        - http://wtforms.simplecodes.com/docs/1.0.1/validators.html
        - http://stackoverflow.com/questions/8463209/how-to-make-a-field-conditionally-optional-in-wtforms

    """
    field_flags = ('requiredif',)

    def __init__(self, other_field_name, message=None, *args, **kwargs):
        self.other_field_name = other_field_name
        self.message = message

    def __call__(self, form, field):
        other_field = form[self.other_field_name]
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if bool(other_field.data):
            super(RequiredIf, self).__call__(form, field)


# Forms
class EmailForm(Form):
    email = StringField('Email', validators=[InputRequired(), Email()])


class PasswordForm(Form):
    password = PasswordField('Contraseña', validators=[
        InputRequired(message='Esto es requerido.')
    ])


class LoginForm(Form):
    email = StringField('Correo electrónico', validators=[
        InputRequired(message='Esto es requerido.'),
        Email(message='No un correo electrónico adecuado.')
    ])
    password = PasswordField('Contraseña', validators=[InputRequired(message='Esto es requerido.')])

    def validate(self):
        initial_validation = super(LoginForm, self).validate()
        if not initial_validation:
            return False
        con = engine.connect()
        user = current_user(con, self.email.data)
        con.close()
        if user is None:
            self.email.errors.append("Este correo electrónico no está registrado")
            return False
        if user.prohibido:
            self.email.errors.append("Esta cuenta ha sido prohibida.")
            return False
        if not bcrypt.verify(str(self.password.data), user.contrasena):
            self.password.errors.append("Contraseña invalida")
            return False
        return True


class RegisterForm(Form):
    # Whether the user is an individual or a Organization affects which fields appear
    user_type = RadioField('Organización o Individuo',
                          validators=[InputRequired(message='Esto es requerido.')],
                          choices=[('persona', 'Un individuo'), ('grupo', 'Una organización')])

    # The minimum required fields to make an account
    nom_usuario = StringField('Nomdre de usuario', validators=[
        InputRequired(message='Esto es requerido.'),
        Length(min=4, max=25),
        Regexp('^[a-zÀ-ÿ0-9_-]+$', message='nombre de usuario debe ser números, letras, guiones o subrayados')
    ])
    email = StringField('Correo electrónico ', validators=[
        InputRequired(message='Esto es requerido.'),
        Length(min=6, max=100),
        Email(message='No un correo electrónico adecuado.')
    ])
    contrasena = PasswordField('Contraseña', validators=[
        InputRequired(message='Esto es requerido.'),
        EqualTo('confirm', message='los paswords no coinciden')
    ])
    confirm = PasswordField('Confirmar Contraseña', [InputRequired(message='Esto es requerido.')])

    def validate(self):
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        con = engine.connect()
        user_email_query = text("""SELECT usuario_id FROM public.usuario WHERE LOWER(gr_email) = LOWER(:email)
                                                                        OR LOWER(pers_email) = LOWER(:email)""")
        user_email = con.execute(user_email_query, email=self.email.data).first()
        username_query = text("""SELECT nom_usuario FROM public.usuario 
                                  WHERE LOWER(nom_usuario) = LOWER(:nom_usuario)""")
        username = con.execute(username_query, nom_usuario=self.nom_usuario.data).first()
        con.close()
        is_valid = True
        if user_email:
            self.email.errors.append("Este correo electrónico ya está registradod")
            is_valid = False
        if username:
            self.nom_usuario.errors.append("Este nombre de usuario ya está registrado")
            is_valid = False
        return is_valid


class OrgForm(Form):
    # Member of organization and title at that organization
    titulo = StringField('Título', validators=[Optional()])
    fecha_comienzo = StringField('Fecha de afiliación', validators=[
        Optional(),
        Date(),
        RequiredIf('fecha_finale'),
        LessThanDate('fecha_finale')
    ])
    fecha_finale = StringField('Fecha de salida', validators=[
        Optional(),
        Date(),
        GreaterThanDate('fecha_comienzo')
    ])
    grupo_id = SelectField('Nom del Organización', validators=[
        InputRequired(message='Esto es requerido.')
    ])


class InfoForm(Form):
    # The optional fields to add additional information to a user
    nom_part = StringField('Nombre', validators=[Optional()])
    nom_paterno = StringField('Apellido paterno', validators=[Optional()])
    nom_materno = StringField('Apellido materno', validators=[Optional()])
    seudonimo = StringField('Seudónimo', validators=[Optional()])
    nom_part_gr = StringField('Nom del Organización', validators=[Optional()])
    sitio_web = StringField('Sitio web', validators=[
        URL(),
        Optional()
    ])

    direccion = StringField('Dirreción postal', validators=[Optional()])
    telefono = StringField('Teléfono', validators=[Optional()])
    fecha_comienzo = StringField('Fecha de comenzando', validators=[
        Optional(),
        Date(),
    ])

    genero = SelectField('Género', validators=[Optional()])

    # Dynamic form for institutions.
    org_form = FieldList(FormField(OrgForm), min_entries=1)

    # If a sublocation is entered, its parent location is required
    ciudad = StringField('Ciudad', validators=[Optional()])
    subdivision = StringField('Estado, provincia o depto.', validators=[RequiredIf('ciudad')])
    pais = SelectField('País', validators=[RequiredIf(other_field_name='subdivision')])

    # if organization just specify type
    tipo_grupo = SelectField('Tipo del Organización', validators=[Optional()])

    coment_part = TextAreaField('Comentarios', validators=[Optional()])


class UpdateEntityForm(InfoForm):
    ciudad_muer = StringField('Ciudad', validators=[Optional()])
    subdivision_muer = StringField('Estado, provincia o depto.', validators=[RequiredIf('ciudad_muer')])
    pais_muer = SelectField('País', validators=[RequiredIf(other_field_name='subdivision_muer')])
    fecha_finale = StringField('Fecha Finale', validators=[
        Optional(),
        Date(),
    ])

    email = StringField('Correo electrónico ', validators=[
        Optional(),
        Email(message='No un correo electrónico adecuado.')
    ])

    def validate(self):
        initial_validation = super(InfoForm, self).validate()
        if not initial_validation:
            return False
        con = engine.connect()
        user_email_query = text("""SELECT usuario_id FROM public.usuario WHERE LOWER(gr_email) = LOWER(:email)
                                                                          OR LOWER(pers_email) = LOWER(:email)""")
        user_email = con.execute(user_email_query, email=self.email.data).first()
        con.close()
        if user_email:
            self.email.errors.append("Este correo electrónico ya está registradod")
            return False
        return True


class AddEntityForm(UpdateEntityForm):
    # Whether the user is an individual or a Organization affects which fields appear
    user_type = RadioField('Organización o Individuo'
                           , validators=[InputRequired(message='Esto es requerido.')]
                           , choices=[('persona', 'Un individuo'), ('grupo', 'Una organización')])


class CopyrightForm(Form):
    cobertura = SelectField('Cobertura', validators=[InputRequired(message='Esto es requerido.')])
    pais_cob = SelectField('País Cobertura', validators=[InputRequired(message='Esto es requerido.')])

    fecha_comienzo_cob = StringField('Fecha Comienzo', validators=[
        Optional(),
        Date(),
        LessThanDate('fecha_finale_cob')
    ])

    fecha_finale_cob = StringField('Fecha Finale', validators=[
        Optional(),
        Date(),
        GreaterThanDate('fecha_comienzo_cob')
    ])


class DynamicAuthorForm(Form):
    # Dynamic form to add any number of authors to AddCompForm
    part_id = SelectField('Artista')
    rol_composicion = SelectField('Papel en esta composición')


class DynamicLangForm(Form):
    # Dynamic form to add any number of languages to AddCompForm
    idioma_id = SelectField('Idiomas en esta composición')


class DynamicThemeForm(Form):
    # Dynamic form to add any number of themes to AddCompForm
    tema_id = SelectField('Temas en esta composición')


class AddCompForm(CopyrightForm):
    # Form to add a composicion
    references = BooleanField("Esta compisicion es una traducción o "
                              "una versión diferente de otra composición en esta base de datos.")
    composicion_id = SelectField('Composición de referencia', validators=[RequiredIf('references')])

    nom_tit = StringField("Título", validators=[InputRequired(message='Esto es requerido.')])
    nom_alt = StringField("Título Alternativo", validators=[Optional()])
    texto = TextAreaField("Texto del Composición", validators=[Optional()])
    fecha_pub = StringField("Fecha de publicación", validators=[
        Optional(),
        Date()
    ])
    part_id_form = FieldList(FormField(DynamicAuthorForm), min_entries=1)
    idioma_form = FieldList(FormField(DynamicLangForm), min_entries=1, validators=[Optional()])
    tema_form = FieldList(FormField(DynamicThemeForm), min_entries=1, validators=[Optional()])


class DynamicInterpForm(Form):
    # Dynamic for to add any number of artists to AddTrackForm
    part_id = SelectField('Artista')
    rol_pista_son = SelectField('Papel en esta pista')
    instrumento_id = SelectField('instrumento')


class DynamicGenMusForm(Form):
    # Dynamic form to add any number of genres to AddTrackForm
    gen_mus_id = SelectField('Género musical en esta pista audio')


class AddTrackForm(CopyrightForm):
    # Add a pista son to the database
    comp_id = SelectField('Composición de referencia', validators=[InputRequired(message='Esto es requerido.')])
    track_no_arr = [(str(i), str(i)) for i in range(1, 100)]
    numero_de_pista = SelectField('Número de pista', choices=track_no_arr, validators=[Optional()])
    medio = SelectField('Medios originales', validators=[Optional()])
    serie_id = SelectField('Serie', validators=[Optional()])

    fecha_grab = StringField("Fecha de grabación", validators=[
        Optional(),
        Date(),
        LessThanDate('fecha_dig')
    ])
    fecha_dig = StringField("Fecha de digitalización", validators=[
        Optional(),
        Date(),
        LessThanDate('fecha_cont')
    ])
    fecha_cont = StringField("Fecha de la donación", validators=[
        Optional(),
        Date()
    ])
    ciudad = StringField('Ciudad', validators=[Optional()])
    subdivision = StringField('Estado, provincia o depto.', validators=[RequiredIf('ciudad')])
    pais = SelectField('País', validators=[RequiredIf(other_field_name='subdivision')])

    archivo = FileField("Subir un archivo")
    gen_mus_form = FieldList(FormField(DynamicGenMusForm), min_entries=1, validators=[Optional()])
    interp_form = FieldList(FormField(DynamicInterpForm), min_entries=1)
    coment_pista_son = TextAreaField("Comentario", validators=[Optional()])


# Forms for the varios tab
class SerieForm(Form):
    # Add a serie to the database
    nom_serie = StringField("Nom", validators=[InputRequired(message='Esto es requerido.')])
    giro = StringField("Giro", validators=[Optional()])
    delete_serie = SelectField("Serie actualmente en la base de datos", validators=[Optional()])


class IdiomaForm(Form):
    # Add a language to the database
    nom_idioma = StringField("Nom", validators=[InputRequired(message='Esto es requerido.')])
    delete_idioma = SelectField("Idioma actualmente en la base de datos", validators=[Optional()])


class GenMusForm(Form):
    # Add a musical genre to the database
    nom_gen_mus = StringField("Nom", validators=[InputRequired(message='Esto es requerido.')])
    delete_gen_mus = SelectField("Genero musical actualmente en la base de datos", validators=[Optional()])
    coment_gen_mus = TextAreaField("Comentario", validators=[Optional()])


class AlbumForm(Form):
    # Add an album to the database
    nom_album = StringField("Nom", validators=[InputRequired(message='Esto es requerido.')])
    serie_id = SelectField("Parte de esta serie", validators=[Optional()])
    delete_album = SelectField("Album actualmente en la base de datos", validators=[Optional()])


class TemaForm(Form):
    # Add a serie to the database
    nom_tema = StringField("Nom", validators=[
        InputRequired(message='Esto es requerido.'),
        Length(min=4, max=25, message='debe tener entre 4 y 25 caracteres'),
        Regexp('^[a-zÀ-ÿ0-9_-]+$', message='Tema debe ser números, letras, guiones o subrayados')
    ])
    delete_tema = SelectField("Tema actualmente en la base de datos", validators=[
        Optional(),
    ])


class InstrForm(Form):
    nom_inst = StringField("Nom", validators=[InputRequired(message='Esto es requerido.')])
    familia_instr_id = SelectField("Familia Instrumento", validators=[InputRequired(message='Esto es requerido.')])
    electronico = BooleanField("Es un instrumento eléctrico")
    instrumento_comentario = TextAreaField("Comentario", validators=[Optional()])
    delete_inst = SelectField("Instrumento actualmente en la base de datos", validators=[Optional()])


class ChangePasswordForm(Form):
    old_password = PasswordField('Introducir contraseña antigua',
                                 validators=[InputRequired(message='Esto es requerido.')])
    new_password = PasswordField('Contraseña', validators=[
        InputRequired(message='Esto es requerido.'),
        EqualTo('confirm', message='los paswords no coinciden')
    ])
    confirm = PasswordField('Confirmar Contraseña',
                            validators=[InputRequired(message='Esto es requerido.')])

    def validate(self):
        from flask import session
        initial_validation = super(ChangePasswordForm, self).validate()
        if not initial_validation:
            return False
        con = engine.connect()
        user_pass = current_user(con, session['email']).contrasena
        con.close()
        if not bcrypt.verify(str(self.old_password.data), user_pass):
            self.old_password.errors.append("Contraseña invalida")
            return False
        return True
