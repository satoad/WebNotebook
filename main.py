from flask import Flask, request, url_for, render_template, redirect
from data import db_session
from flask_bcrypt import Bcrypt
from data.users import User

app = Flask(__name__)
bcrypt = Bcrypt(app)


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
    return render_template('index.html', **param)


@app.route('/signin', methods=['POST', 'GET'])
def signin():
    param = {}
    param['bootstrap'] = url_for('static', filename='css/bootstrap.min.css')
    param['style'] = url_for('static', filename='css/style.css')
    param['clouds'] = url_for('static', filename='sources/icons/clouds.svg')
    if request.method == 'POST':
        if request.form['upassword'] != request.form['upassword-confirm']:
            # /todo Добавить поле для сообщений об ошибках
            return render_template('signin.html', **param)
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == request.form['uemail']).first():
            # /todo Добавить поле для сообщений об ошибках
            return render_template('signin.html', **param)
        user = User(
            name=request.form['uname'],
            email=request.form['uemail']
        )
        user.set_password(request.form['upassword'])
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('signin.html', **param)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        param = {}
        param['bootstrap'] = url_for('static', filename='css/bootstrap.min.css')
        param['style'] = url_for('static', filename='css/style.css')
        param['clouds'] = url_for('static', filename='sources/icons/clouds.svg')
        return render_template('login.html', **param)
    elif request.method == 'POST':
        print(request.form['email'])
        print(request.form['password'])
        print(request.form['class'])
        print(request.form['file'])
        print(request.form['about'])
        print(request.form['accept'])
        print(request.form['sex'])
        return "Форма отправлена"


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


if __name__ == '__main__':
    db_session.global_init("db/users.db")
    app.run(port=8080, host='127.0.0.1')