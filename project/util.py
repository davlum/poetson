# project/util.py

from flask_mail import Message
from flask import session
from sqlalchemy import text
from project import app, mail
from re import compile


def current_user(con, email):
    query = text("""SELECT * FROM part_us WHERE LOWER(email)=LOWER(:email)""")
    result = con.execute(query, email=email).first()
    return result


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
        ("'01/" + d + "'", 'MONTH')
    if full.match(d):
        return ("'" + d + "'", 'FULL')


def current_org(con, email):
    query = text("""SELECT * FROM part_us_ag WHERE LOWER(email)=LOWER(:email)""")
    result = con.execute(query, email=email).first()
    return result


def current_pers(con, email):
    query = text("""SELECT * FROM part_us_pers WHERE LOWER(email)=LOWER(:email)""")
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
