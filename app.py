from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for, session, logging, request
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from data import Articles
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt


app = Flask(__name__, static_url_path='/static')
app.config.from_pyfile('config.py')

Articles = Articles()

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    name = db.Column(db.Text)
    email = db.Column(db.Text)
    username = db.Column(db.Text)
    password = db.Column(db.Text)
    register_date = db.Column(db.Date, nullable=False,
            default=datetime.utcnow())

    def __init__(self, name, email, username, password):
        self.name = name
        self.email = email
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/searchall/')
def searchall():
    return render_template('searchAll.html')

@app.route('/articles')
def articles():
    return render_template('articles.html', articles=Articles)


@app.route('/article/<string:id>/')
def article(id):
    return render_template('article.html', id=id)


class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        
        usr = Users(name, email, username, password)
        db.session.add(usr)
        db.session.commit()
        
        flash('You are now registered and can login', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']

        result = Users.query.filter_by(usrname=username).first()
        if result is not None:
            if sha256_crypt.verify(password_candidate, result.password):
                session['logged_in'] = True
                session['username'] = username
                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                app.logger.info('PASSWORD NOT MATCHED', error=error)
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')




if __name__ == '__main__':
    manager.run()
