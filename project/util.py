# project/util.py


from flask_testing import TestCase
from project import app, db
from project.models import User
from flask_mail import Message
from project import app, mail


def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)


class BaseTestCase(TestCase):

    def create_app(self):
        app.config.from_object('project.config.TestingConfig')
        return app

    def setUp(self):
        db.create_all()
        user = User(email="ad@min.com", password="admin_user", confirmed=False)
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
