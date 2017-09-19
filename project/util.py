# project/util.py
# coding=utf-8

from flask_mail import Message
from sqlalchemy import text
from project import app, mail
from re import compile
from flask import session

def current_user(con, email):
    query = text("""SELECT * 
                      FROM public.usuario 
                      WHERE LOWER(gr_email)=LOWER(:email)
                         OR LOWER(pers_email)=LOWER(:email)""")
    result = con.execute(query, email=email).first()
    return result


def allowed_file(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    return '.' in filename and ext in app.config['ALLOWED_EXTENSIONS']


def send_email(to, subject, template):
    message = '¡Bienvenido! Gracias por registrarte. Siga este enlace para activar su cuenta:'
    msg = Message(
        subject,
        body=message,
        recipients=[to],
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)


# Return a pretty printed date from
# the fecha UDT
def get_fecha(fecha):
    if fecha is None:
        return None
    fecha, type = tuple(fecha[1:-1].split(','))
    fecha = fecha.split('-')
    if type == 'YEAR':
        return fecha[0]
    if type == 'MONTH':
        return fecha[1]+'/'+fecha[0]
    if type == 'FULL':
        return fecha[2]+'/'+fecha[1]+'/'+fecha[0]


# Properly parses a date-like string
# into the UDT fecha
def parse_fecha(d):
    d = d.strip(' ')
    if d == '':
        return None
    year = compile('^\d{4}$')
    month = compile('^\d{1,2}\/\d{4}$')
    full = compile('^\d{1,2}\/\d{1,2}\/\d{4}$')
    if year.match(d):
        return ("'01/01/" + d + "'", 'YEAR')
    if month.match(d):
        return ("'01/" + d + "'", 'MONTH')
    if full.match(d):
        return ("'" + d + "'", 'FULL')


def current_gr(con, email):
    query = text("""SELECT * FROM public.us_gr WHERE LOWER(email)=LOWER(:email)""")
    result = con.execute(query, email=email).first()
    return result


def current_pers(con, email):
    query = text("""SELECT * FROM public.us_pers WHERE LOWER(email)=LOWER(:email)""")
    result = con.execute(query, email=email).first()
    return result



#class BaseTestCase(TestCase):
#
#    def create_app(self):
#        app.config.from_object('project.config.TestingConfig')
#        return app
#
#    def setUp(self):
#        db.create_all()
#        user = User(email="ad@min.com", password="admin_user", confirmed=False)
#        db.session.add(user)
#        db.session.commit()
#
#    def tearDown(self):
#        db.session.remove()
#        db.drop_all()
