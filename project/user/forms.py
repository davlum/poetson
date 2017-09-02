# project/user/forms.py


from flask_wtf import Form
from wtforms import StringField, PasswordField, RadioField, TextAreaField, DateField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, InputRequired, Optional, URL
from project import db

class EmailForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email()])

class PasswordForm(Form):
    password = PasswordField('Password', validators=[DataRequired()])

class LoginForm(Form):
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])


class RegisterForm(Form):

    # The minimum required fields to make an account
    username = StringField('Nomdre del usario', [
        InputRequired(message='Esto es requerido.'),
        Length(min=4, max=25),
    ])
    email = StringField('Email', [
        InputRequired(message='Esto es requerido.'),
        Length(min=6, max=100),
        Email()
    ])
    password = PasswordField('Contrasena', [
        InputRequired(message='Esto es requerido.'),
        EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirmar Contrasena', [InputRequired(message='Esto es requerido.')])

    # The optional fields to add additional information to a user
    userType = RadioField('Organizacion o individuo',
                          [Optional()],
                          choices=[(1, 'Individuo'), (0, 'Organizacion')])
    firstName = StringField('Nom Primero', [Optional()])
    lastName = StringField('Nom Segundo', [Optional()])
    pseudonym = StringField('Seudonimo', [Optional()])
    website = StringField('Sitio Web', [
        URL(),
        Optional()
    ])
    # Get List of possible agregate types
    agQuery = ("""SELECT nom_tipo_agregar nom FROM tipo_agregar;""")
    agResult = db.engine.execute(agQuery)
    agArr = [(res.nom, res.nom) for res in agResult]

    # Get List of possible genders
    genderQuery = ("""SELECT nom_genero nom FROM genero_persona;""")
    genderResult = db.engine.execute(genderQuery)
    genderArr = [(res.nom, res.nom) for res in genderResult]

    address = StringField('Dirrecion', [Optional()])
    telephone = StringField('Telefono', [Optional()])
    dob = DateField('Fecha Nac - dd/mm/aaaa', format='%d/%m/%y')
    gender = SelectField('Genero', choices=genderArr)
    city = StringField('Ciudad')
    state = StringField('Estado')
    country = StringField('Pais')
    comment = TextAreaField('Comentario')
    member = SelectField('Tipo del Organizacion', choices=agArr)
    title = StringField('Titulo')
    dadName = StringField('Nombre del Paterno', [Optional()])
    momName = StringField('Nombre del Materno', [Optional()])

    def validate(self):
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        userQuery = ("""SELECT email FROM usario WHERE email=:email""")
        user = db.engine.execute(userQuery, email=self.email.data).first()
        if user:
            self.email.errors.append("Email already registered")
            return False
        return True


class ChangePasswordForm(Form):
    password = PasswordField(
        'password',
        validators=[DataRequired(), Length(min=6, max=25)]
    )
    confirm = PasswordField(
        'Repeat password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match.')
        ]
    )
