# project/user/forms.py


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
            print('regex failed')
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
        user = current_user(self.email.data)
        if user is None:
            self.email.errors.append("Este correo electrónico no está registrado")
            return False
        if not bcrypt.verify(str(self.password.data), user.contrasena):
            self.password.errors.append("Contraseña invalida")
            return False
        return True


class OrgForm(Form):
    con = engine.connect()
    ag_query = text("""SELECT pa_id, nom_part FROM public.part_ag;""")
    ag_result = con.execute(ag_query)
    ag_arr = [(str(res.pa_id), res.nom_part) for res in ag_result]
    ag_arr.insert(0, ('0', 'Ninguno'))
    con.close()
    # Member of organization and title at that organization
    nom_ag = SelectField('Nom del Organización', choices=ag_arr, validators=[Optional()])
    title = StringField('Título', validators=[Optional()])
    date_joined = StringField('Comienzo', validators=[
        Optional(),
        Date(),
        RequiredIf('date_left')
    ])
    date_left = StringField('Finale', validators=[
        Optional(),
        Date(),
    ])


class RegisterForm(Form):

    # Whether the user is an individual or a Organization affects which fields appear
    user_type = RadioField('Organización o Individuo',
                          validators=[InputRequired(message='Esto es requerido.')],
                          choices=[('0', 'Individuo'), ('1', 'Organización')])


    # The minimum required fields to make an account
    username = StringField('Nomdre del usario', validators=[
        InputRequired(message='Esto es requerido.'),
        Length(min=4, max=25),
        Regexp('^[a-zÀ-ÿ0-9_-]+$', message='nombre de usuario debe ser números, letras, guiones o subrayados')
    ])
    email = StringField('Email', validators=[
        InputRequired(message='Esto es requerido.'),
        Length(min=6, max=100),
        Email(message='No un correo electrónico adecuado.')
    ])
    password = PasswordField('Contraseña', validators=[
        InputRequired(message='Esto es requerido.'),
        EqualTo('confirm', message='los paswords no coinciden')
    ])
    confirm = PasswordField('Confirmar Contraseña', [InputRequired(message='Esto es requerido.')])

    def validate(self):
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        con = engine.connect()
        user_email_query = text("""SELECT email FROM part_us WHERE email ILIKE :email""")
        user_email = con.execute(user_email_query, email=self.email.data).first()
        username_query = text("""SELECT nom_usario FROM part_us WHERE nom_usario ILIKE :username""")
        username = con.execute(username_query, username=self.username.data).first()
        con.close()
        is_valid = True
        if user_email:
            self.email.errors.append("Este correo electrónico ya está registradod")
            is_valid = False
        if username:
            self.username.errors.append("Este nombre de usuario ya está registrado")
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
    first_name = StringField('Nombre de Pila', validators=[Optional()])
    last_name = StringField('Apellido', validators=[Optional()])
    pseudonym = StringField('Seudónimo', validators=[Optional()])
    org_name = StringField('Nom del Organización', validators=[Optional()])
    website = StringField('Sitio Web', validators=[
        URL(),
        Optional()
    ])

    address = StringField('Dirreción', validators=[Optional()])
    telephone = StringField('Teléfono', validators=[Optional()])
    dob = StringField('Fecha de Nacimiento', validators=[
        Optional(),
        Date()
    ])
    date_formed = StringField('Fecha Formado', validators=[
        Optional(),
        Date()
    ])
    gender = SelectField('Género', choices=gender_arr, validators=[Optional()])

    # Dynamic form for institutions.
    org_form = FieldList(FormField(OrgForm))

    # If a sublocation is entered, its parent location is required
    city = StringField('Ciudad', validators=[Optional()])
    subdiv = StringField('Subdivision', validators=[RequiredIf('city')])
    subdiv_type = SelectField('Tipo del Subdivision', choices=subdiv_arr, validators=[RequiredIf(other_field_name='subdiv')])
    country = SelectField('País', choices=country_arr, validators=[RequiredIf(other_field_name='subdiv_type')])

    # if organization just specify type
    tipo_ag = SelectField('Tipo del Organización', choices=tipo_ag_arr, validators=[Optional()])

    comment = TextAreaField('Comentarios', validators=[Optional()])
    dad_name = StringField('Nombre del Padre', validators=[Optional()])
    mom_name = StringField('Nombre del Madre', validators=[Optional()])

    def validate(self):
        initial_validation = super(InfoForm, self).validate()
        if not initial_validation:
            return False
        return True

class AddEntityForm(InfoForm):
    # Whether the user is an individual or a Organization affects which fields appear
    user_type = RadioField('Organización o Individuo',
                          validators=[InputRequired(message='Esto es requerido.')],
                          choices=[('0', 'Individuo'), ('1', 'Organización')])


class AddTrackForm(Form):
    con =  engine.connect()
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
    con.close()

    # Does this track reference a composition already in the database
    references = BooleanField("""¿Esta pista de audio hace referencia a 
                                una composición ya en nuestra base de datos?""")
    title = StringField("Título", validators=[InputRequired(message='Esto es requerido.')])
    alt_title = StringField("Título Alternativo", validators=[Optional()])
    text = TextAreaField("Texto", validators=[Optional()])
    date_published = DateField("Fecha de publicación", format='d%/%m/%Y', validators=[Optional()])

    comp_city = StringField('Ciudad', validators=[Optional()])
    comp_subdiv = StringField('Subdivision', validators=[RequiredIf('comp_city')])
    comp_subdiv_type = SelectField('Tipo del Subdivision', choices=subdiv_arr,
                              validators=[RequiredIf(other_field_name='comp_subdiv')])
    comp_country = SelectField('País', choices=country_arr, 
                               validators=[RequiredIf(other_field_name='comp_subdiv_type')])

    track_no_arr = [(str(i), str(i)) for i in range(1, 100)]
    track_no = SelectField('Número de pista', choices=track_no_arr, validators=[Optional()])
    medio = SelectField('Medios originales', choices=medio_arr, validators=[Optional()])
    date_recorded = StringField("Fecha registrada", validators=[
        Optional(),
        Date()
    ])

    date_digitized = StringField("Fecha digitalizada", validators=[
        Optional(),
        Date()
    ])

    interp_city = StringField('Ciudad', validators=[Optional()])
    interp_subdiv = StringField('Subdivision', validators=[RequiredIf('interp_city')])
    interp_subdiv_type = SelectField('Tipo del Subdivision', choices=subdiv_arr,
                                   validators=[RequiredIf(other_field_name='interp_subdiv')])
    interp_country = SelectField('País', choices=country_arr,
                               validators=[RequiredIf(other_field_name='interp_subdiv_type')])

    audio_file = FileField("Archivo de audio", validators=[InputRequired(message='Esto es requerido.')])

    comments = TextAreaField("Commentario", validators=[Optional()])


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
