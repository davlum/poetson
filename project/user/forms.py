# project/user/forms.py
# coding=utf-8

from wtforms import Form, StringField, PasswordField, RadioField, \
    TextAreaField, DateField, SelectField, BooleanField, FileField, FieldList, FormField
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
    email = StringField('Email', validators=[
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
        if not bcrypt.verify(str(self.password.data), user.contrasena):
            self.password.errors.append("Contraseña invalida")
            return False
        return True


class OrgForm(Form):
    con = engine.connect()
    ag_query = text("""SELECT part_id, nom_part FROM public.agregar;""")
    ag_result = con.execute(ag_query)
    ag_arr = [(str(res.part_id), res.nom_part) for res in ag_result]
    ag_arr.insert(0, ("0", 'Ninguno'))
    con.close()
    # Member of organization and title at that organization
    agregar_id = SelectField('Nom del Organización', choices=ag_arr, validators=[Optional()])
    titulo = StringField('Título', validators=[Optional()])
    fecha_comienzo = StringField('Comienzo', validators=[
        Optional(),
        Date(),
        RequiredIf('fecha_finale')
    ])
    fecha_finale = StringField('Finale', validators=[
        Optional(),
        Date(),
    ])


class RegisterForm(Form):

    # Whether the user is an individual or a Organization affects which fields appear
    user_type = RadioField('Organización o Individuo',
                          validators=[InputRequired(message='Esto es requerido.')],
                          choices=[('persona', 'Individuo'), ('agregar', 'Organización')])

    # The minimum required fields to make an account
    nom_usario = StringField('Nomdre del usario', validators=[
        InputRequired(message='Esto es requerido.'),
        Length(min=4, max=25),
        Regexp('^[a-zÀ-ÿ0-9_-]+$', message='nombre de usuario debe ser números, letras, guiones o subrayados')
    ])
    email = StringField('Email', validators=[
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
        user_email_query = text("""SELECT usario_id FROM public.usario WHERE LOWER(ag_email) = LOWER(:email)
                                                                        OR LOWER(pers_email) = LOWER(:email)""")
        user_email = con.execute(user_email_query, email=self.email.data).first()
        username_query = text("""SELECT nom_usario FROM public.usario WHERE LOWER(nom_usario) = LOWER(:nom_usario)""")
        username = con.execute(username_query, nom_usario=self.nom_usario.data).first()
        con.close()
        is_valid = True
        if user_email:
            self.email.errors.append("Este correo electrónico ya está registradod")
            is_valid = False
        if username:
            self.nom_usario.errors.append("Este nombre de usuario ya está registrado")
            is_valid = False
        return is_valid


class InfoForm(Form):
    
    con = engine.connect()
    # Get List of possible agregate types
    tipo_ag_query = text("""SELECT nom_tipo_agregar nom FROM public.tipo_agregar;""")
    tipo_ag_result = con.execute(tipo_ag_query)
    tipo_ag_arr = [(res.nom, res.nom) for res in tipo_ag_result]

    # Get List of possible genders
    gender_query = text("""SELECT nom_genero FROM public.genero_persona;""")
    gender_result = con.execute(gender_query)
    gender_arr = [(str(res.nom_genero), res.nom_genero) for res in gender_result]

    # Get List of subdivisions
    subdiv_query = text("""SELECT tipo_subdiv nom FROM public.tipo_subdivision;""")
    subdiv_result = con.execute(subdiv_query)
    subdiv_arr = [(res.nom, res.nom) for res in subdiv_result]
    # Get List of countries
    country_query = text("""SELECT nom_pais FROM public.pais;""")
    country_result = con.execute(country_query)
    country_arr = [(res.nom_pais, res.nom_pais) for res in country_result]
    con.close()

    # The optional fields to add additional information to a user
    nom_part = StringField('Nombre de Pila', validators=[Optional()])
    nom_segundo = StringField('Apellido', validators=[Optional()])
    seudonimo = StringField('Seudónimo', validators=[Optional()])
    nom_part_ag = StringField('Nom del Organización',
                              validators=[Optional()])
    sitio_web = StringField('Sitio Web', validators=[
        URL(),
        Optional()
    ])

    direccion = StringField('Dirreción', validators=[Optional()])
    telefono = StringField('Teléfono', validators=[Optional()])
    fecha_comienzo = StringField('Fecha de comenzando', validators=[
        Optional(),
        Date()
    ])

    genero = SelectField('Género', choices=gender_arr, validators=[Optional()])

    # Dynamic form for institutions.
    org_form = FieldList(FormField(OrgForm), min_entries=1)

    # If a sublocation is entered, its parent location is required
    ciudad = StringField('Ciudad', validators=[Optional()])
    nom_subdivision = StringField('Subdivision', validators=[RequiredIf('ciudad')])
    tipo_subdivision = SelectField('Tipo del Subdivision', choices=subdiv_arr
                                   , validators=[RequiredIf(other_field_name='nom_subdivision')])
    pais = SelectField('País', choices=country_arr
                       , validators=[RequiredIf(other_field_name='tipo_subdivision')])

    # if organization just specify type
    tipo_agregar = SelectField('Tipo del Organización', choices=tipo_ag_arr, validators=[Optional()])

    coment_part = TextAreaField('Comentarios', validators=[Optional()])
    nom_paterno = StringField('Nombre del Padre', validators=[Optional()])
    nom_materno = StringField('Nombre del Madre', validators=[Optional()])

    def validate(self):
        initial_validation = super(InfoForm, self).validate()
        if not initial_validation:
            return False
        return True


class AddEntityForm(InfoForm):
    con = engine.connect()
    # Get List of subdivisions
    subdiv_query = text("""SELECT tipo_subdiv nom FROM public.tipo_subdivision;""")
    subdiv_result = con.execute(subdiv_query)
    subdiv_arr = [(res.nom, res.nom) for res in subdiv_result]
    # Get List of countries
    country_query = text("""SELECT nom_pais FROM public.pais;""")
    country_result = con.execute(country_query)
    country_arr = [(res.nom_pais, res.nom_pais) for res in country_result]
    con.close()

    # Whether the user is an individual or a Organization affects which fields appear
    user_type = RadioField('Organización o Individuo',
                          validators=[InputRequired(message='Esto es requerido.')],
                          choices=[('persona', 'Individuo'), ('agregar', 'Organización')])
    ciudad_muer = StringField('Ciudad', validators=[Optional()])
    nom_subdivision_muer = StringField('Subdivision', validators=[RequiredIf('ciudad_muer')])
    tipo_subdivision_muer = SelectField('Tipo del Subdivision', choices=subdiv_arr
                                   , validators=[RequiredIf(other_field_name='nom_subdivision_muer')])
    pais_muer = SelectField('País', choices=country_arr
                       , validators=[RequiredIf(other_field_name='tipo_subdivision_muer')])
    fecha_finale = StringField('Fecha Finale', validators=[
        Optional(),
        Date()
    ])

    email = StringField('Email', validators=[
        Optional(),
        Email(message='No un correo electrónico adecuado.')
    ])

    def validate(self):
        initial_validation = super(InfoForm, self).validate()
        if not initial_validation:
            return False
        con = engine.connect()
        user_email_query = text("""SELECT usario_id FROM public.usario WHERE LOWER(ag_email) = LOWER(:email)
                                                                          OR LOWER(pers_email) = LOWER(:email)""")
        user_email = con.execute(user_email_query, email=self.email.data).first()
        con.close()
        if user_email:
            self.email.errors.append("Este correo electrónico ya está registradod")
            return False
        return True


class UpdateEntityForm(InfoForm):
    con = engine.connect()
    # Get List of subdivisions
    subdiv_query = text("""SELECT tipo_subdiv nom FROM public.tipo_subdivision;""")
    subdiv_result = con.execute(subdiv_query)
    subdiv_arr = [(res.nom, res.nom) for res in subdiv_result]
    # Get List of countries
    country_query = text("""SELECT nom_pais FROM public.pais;""")
    country_result = con.execute(country_query)
    country_arr = [(res.nom_pais, res.nom_pais) for res in country_result]
    con.close()

    ciudad_muer = StringField('Ciudad', validators=[Optional()])
    nom_subdivision_muer = StringField('Subdivision', validators=[RequiredIf('ciudad_muer')])
    tipo_subdivision_muer = SelectField('Tipo del Subdivision', choices=subdiv_arr
                                   , validators=[RequiredIf(other_field_name='nom_subdivision_muer')])
    pais_muer = SelectField('País', choices=country_arr
                       , validators=[RequiredIf(other_field_name='tipo_subdivision_muer')])
    fecha_finale = StringField('Fecha Finale', validators=[
        Optional(),
        Date()
    ])

    email = StringField('Email', validators=[
        Optional(),
        Email(message='No un correo electrónico adecuado.')
    ])

    def validate(self):
        initial_validation = super(InfoForm, self).validate()
        if not initial_validation:
            return False
        con = engine.connect()
        user_email_query = text("""SELECT usario_id FROM public.usario WHERE LOWER(ag_email) = LOWER(:email)
                                                                          OR LOWER(pers_email) = LOWER(:email)""")
        user_email = con.execute(user_email_query, email=self.email.data).first()
        con.close()
        if user_email:
            self.email.errors.append("Este correo electrónico ya está registradod")
            return False
        return True


class DynamicAuthorForm(Form):
    con = engine.connect()
    part_id_query = text("""SELECT part_id, nom_part FROM public.part_view""")
    part_id_result = con.execute(part_id_query)
    part_id_arr = [(str(res.part_id), res.nom_part) for res in part_id_result]

    rol_query = text("""SELECT nom_rol_comp FROM public.rol_composicion""")
    rol_result = con.execute(rol_query)
    rol_arr = [(res.nom_rol_comp, res.nom_rol_comp) for res in rol_result]
    con.close()
    part_id = SelectField('Artista', choices=part_id_arr)
    rol_composicion = SelectField('Papel en esta composición', choices=rol_arr)


class DynamicLangForm(Form):
    con = engine.connect()
    idioma_query = text("""SELECT idioma_id, nom_idioma FROM public.idioma""")
    idioma_result = con.execute(idioma_query)
    idioma_arr = [(str(res.idioma_id), res.nom_idioma) for res in idioma_result]
    idioma_arr.insert(0, ("0", 'Ninguno'))
    con.close()
    idioma_id = SelectField('Idiomas en esta composición', choices=idioma_arr)


class DynamicThemeForm(Form):
    con = engine.connect()
    tema_query = text("""SELECT tema_id, nom_tema FROM public.tema""")
    tema_result = con.execute(tema_query)
    tema_arr = [(str(res.tema_id), res.nom_tema) for res in tema_result]
    tema_arr.insert(0, ("0", 'Ninguno'))
    con.close()
    tema_id = SelectField('Temas en esta composición', choices=tema_arr)


class AddCompForm(Form):
    con = engine.connect()
    comp_query = text("""SELECT composicion_id, nom_tit FROM public.composicion""")
    comp_result = con.execute(comp_query)
    comp_arr = [(str(res.composicion_id), res.nom_tit) for res in comp_result]
    comp_arr.insert(0, ("0", 'Ninguno'))
    con.close()

    references = BooleanField("Esta compisicion es una traducción o "
                              "una versión diferente de otra composición en esta base de datos.")
    comp_id = SelectField('Composición de referencia', choices=comp_arr,
                          validators=[RequiredIf('references')])

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
    con = engine.connect()

    instrumento_query = text("""SELECT instrumento_id, nom_inst FROM public.instrumento""")
    instrumento_result = con.execute(instrumento_query)
    instrumento_arr = [(str(res.instrumento_id), res.nom_inst) for res in instrumento_result]

    part_id_query = text("""SELECT part_id, nom_part FROM public.part_view""")
    part_id_result = con.execute(part_id_query)
    part_id_arr = [(str(res.part_id), res.nom_part) for res in part_id_result]

    rol_query = text("""SELECT nom_rol_pista FROM public.rol_pista_son""")
    rol_result = con.execute(rol_query)
    rol_arr = [(res.nom_rol_pista, res.nom_rol_pista) for res in rol_result]
    print('rol_arr')
    con.close()
    part_id = SelectField('Artista', choices=part_id_arr)
    rol_pista_son = SelectField('Papel en esta pista', choices=rol_arr)
    instrumento_id = SelectField('instrumento', choices=instrumento_arr)


class DynamicGenMusForm(Form):
    con = engine.connect()
    gen_mus_query = text("""SELECT gen_mus_id, nom_gen_mus FROM public.genero_musical""")
    gen_mus_result = con.execute(gen_mus_query)
    gen_mus_arr = [(str(res.gen_mus_id), res.nom_gen_mus) for res in gen_mus_result]
    gen_mus_arr.insert(0, ("0", 'Ninguno'))
    con.close()
    gen_mus_id = SelectField('Género musical en esta pista audio', choices=gen_mus_arr)


class AddTrackForm(Form):
    con = engine.connect()
    # Get List of subdivisions
    subdiv_query = text("""SELECT tipo_subdiv nom FROM public.tipo_subdivision;""")
    subdiv_result = con.execute(subdiv_query)
    subdiv_arr = [(res.nom, res.nom) for res in subdiv_result]
    # Get List of countries
    country_query = text("""SELECT nom_pais FROM public.pais;""")
    country_result = con.execute(country_query)
    country_arr = [(res.nom_pais, res.nom_pais) for res in country_result]

    medio_query = text("""SELECT nom_medio FROM public.medio;""")
    medio_result = con.execute(medio_query)
    medio_arr = [(res.nom_medio, res.nom_medio) for res in medio_result]

    serie_query = text("""SELECT serie_id, nom_serie FROM public.serie;""")
    serie_result = con.execute(serie_query)
    serie_arr = [(str(res.serie_id), res.nom_serie) for res in serie_result]
    serie_arr.insert(0, ("0", 'Ninguno'))

    comp_query = text("""SELECT composicion_id, nom_tit FROM public.composicion""")
    comp_result = con.execute(comp_query)
    comp_arr = [(str(res.composicion_id), res.nom_tit) for res in comp_result]
    con.close()

    comp_id = SelectField('Composición de referencia', choices=comp_arr,
                          validators=[InputRequired(message='Esto es requerido.')])
    track_no_arr = [(str(i), str(i)) for i in range(1, 100)]
    numero_de_pista = SelectField('Número de pista', choices=track_no_arr, validators=[Optional()])
    medio = SelectField('Medios originales', choices=medio_arr, validators=[Optional()])
    serie_id = SelectField('Serie', choices=serie_arr, validators=[Optional()])

    fecha_grab = StringField("Fecha registrada", validators=[
        Optional(),
        Date()
    ])
    fecha_dig = StringField("Fecha digitalizada", validators=[
        Optional(),
        Date()
    ])
    fecha_cont = StringField("Fecha digitalizada", validators=[
        Optional(),
        Date()
    ])
    ciudad = StringField('Ciudad', validators=[Optional()])
    nom_subdivision = StringField('Subdivision', validators=[RequiredIf('ciudad')])
    tipo_subdivision = SelectField('Tipo del Subdivision', choices=subdiv_arr,
                                   validators=[RequiredIf(other_field_name='nom_subdivision')])
    pais = SelectField('País', choices=country_arr,
                               validators=[RequiredIf(other_field_name='tipo_subdivision')])

    archivo = FileField("Archivo de audio", validators=[InputRequired(message='Esto es requerido.')])
    gen_mus_form = FieldList(FormField(DynamicGenMusForm), min_entries=1, validators=[Optional()])
    interp_form = FieldList(FormField(DynamicInterpForm), min_entries=1)
    coment_pista_son = TextAreaField("Commentario", validators=[Optional()])


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
        user_pass = current_user(session['email']).contrasena
        if not bcrypt.verify(str(self.old_password.data), user_pass):
            self.old_password.errors.append("Contraseña invalida")
            return False
        return True
