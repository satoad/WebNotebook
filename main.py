from flask import Flask, request, url_for, render_template, redirect, session
from data import db_session
from data.users import User
from forms.signinform import SigninForm
from forms.loginform import LoginForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
@app.route('/index')
def index():
    param = {}
    param['bootstrap'] = url_for('static', filename='css/bootstrap.min.css')
    param['style'] = url_for('static', filename='css/style.css')
    param['clouds'] = url_for('static', filename='sources/icons/clouds.svg')
    param['circle'] = url_for('static', filename='sources/icons/person-circle.svg')
    param['user_js'] = url_for('static', filename='scripts/user.js')
    param['bootstrap_js'] = url_for('static', filename='scripts/bootstrap.bundle.min.js')
    param['plus'] = url_for('static', filename='sources/icons/plus.svg')
    param['doc'] = url_for('static', filename='sources/icons/doc.svg')
    param['three_dots'] = url_for('static', filename='sources/icons/three-dots-vertical.svg')
    param['authorized'] = current_user.is_authenticated
    if current_user.is_authenticated:
        param['username'] = current_user.name
    return render_template('index.html', **param)


@app.route('/signin', methods=['POST', 'GET'])
def signin():
    form = SigninForm()
    param = {}
    param['bootstrap'] = url_for('static', filename='css/bootstrap.min.css')
    param['style'] = url_for('static', filename='css/style.css')
    param['clouds'] = url_for('static', filename='sources/icons/clouds.svg')
    param['form'] = form
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            param['message'] = 'Пароли не совпадают'
            return render_template('signin.html', **param)
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            param['message'] = "Такой пользователь уже есть"
            return render_template('register.html', **param)
        user = User(
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('signin.html', **param)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    param = {}
    param['bootstrap'] = url_for('static', filename='css/bootstrap.min.css')
    param['style'] = url_for('static', filename='css/style.css')
    param['clouds'] = url_for('static', filename='sources/icons/clouds.svg')
    param['form'] = form
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect("/")
        param['message'] = 'Неверный логин или пароль'
        return render_template('login.html', **param)
    return render_template('login.html', **param)


@app.route('/notebook')
def notebook():
    param = {}
    param['bootstrap'] = url_for('static', filename='css/bootstrap.min.css')
    param['style'] = url_for('static', filename='css/style.css')
    param['clouds'] = url_for('static', filename='sources/icons/clouds.svg')
    param['circle'] = url_for('static', filename='sources/icons/person-circle.svg')
    param['user_js'] = url_for('static', filename='scripts/user.js')
    param['geometriya'] = url_for('static', filename='sources/test-pdf/geometrija-7-9-kl_-atanasjan.pdf')
    return render_template('notebook.html', **param)


@app.route('/profile')
def profile():
    param = {}
    param['bootstrap'] = url_for('static', filename='css/bootstrap.min.css')
    param['style'] = url_for('static', filename='css/style.css')
    param['clouds'] = url_for('static', filename='sources/icons/clouds.svg')
    return render_template('profile.html', **param)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    db_session.global_init("db/users.db")
    app.run(port=8080, host='127.0.0.1')