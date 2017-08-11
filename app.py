from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for, session, logging, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, create_engine
import psycopg2
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from data import Articles
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps


app = Flask(__name__, static_url_path='/static')
app.config.from_pyfile('config.py')

Articles = Articles()

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/searchhome')
def searchhome():
    return render_template('searchhome.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    result_authors = []
    if request.method == "POST":
        param = request.form["search-main"]
        authors_query = text("""SELECT * FROM public.artista WHERE nom_primero ~* :name OR 
                          nom_segundo ~* :name;""");
        result_authors = db.engine.execute(authors_query, name=param)
    return render_template('search.html', result=result_authors)


@app.route('/articles')
def articles():
    return render_template('articles.html', articles=Articles)


@app.route('/article/<string:articleid>/')
def article(articleid):
    return render_template('article.html', articleid=articleid)


@app.route('/autor/<string:autorid>/')
def autor(autorid):
    author_query = text("""SELECT * FROM public.artista WHERE autor_id=:id """)
    author_result = db.engine.execute(author_query, id=autorid).first()
    lugar_nac_query = text("""SELECT * FROM public.lugar WHERE lugar_id=:id """)
    lugar_nac_result = db.engine.execute(lugar_nac_query, id=author_result.lugar_nac).first()
    print(lugar_nac_result.nom_subdivision)
    lugar_muer_query = text("""SELECT * FROM public.lugar WHERE lugar_id=:id """)
    lugar_muer_result = db.engine.execute(lugar_muer_query, id=author_result.lugar_muer).first()
    return render_template('autor.html', autor=author_result, nac=lugar_nac_result, muer=lugar_muer_result).encode("utf-8")


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

        stmt = text("""INSERT INTO public.editor (email, nom, clave) VALUES 
                        (:email, :name, :password);""")
        db.engine.execute(stmt, email=email, name=name, password=password)

        flash('You are now registered and can login', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password_candidate = request.form['password']

        stmt = text("SELECT * FROM public.editor WHERE email=:email ")
        result = db.engine.execute(stmt, email=email).first()
        if result is not None:
            if sha256_crypt.verify(password_candidate, result.clave):
                session['logged_in'] = True
                session['email'] = email
                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                app.logger.info('PASSWORD NOT MATCHED', error=error)
        else:
            error = 'Email not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

if __name__ == '__main__':
    manager.run()
