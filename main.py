from flask import Flask, request, url_for, render_template, redirect, session, jsonify, send_file
from data import db_session
from data.users import User
from data.files import Files
from forms.signinform import SigninForm
from forms.loginform import LoginForm
from forms.changepassform import ChangepassForm
from forms.fileuploadform import FileuploadForm
from pdfedit import connect_pdf
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import io, os, shutil

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'



@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = FileuploadForm()
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
    param['form'] = form
    param['notebooks'] = []
    if current_user.is_authenticated:
        param['username'] = current_user.name
        param['notebooks'] = current_user.files
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        f = form.file.data
        filename = secure_filename(f.filename)
        dirname = current_user.name + "_" + form.name.data
        filename = form.name.data + '_01'
        file = Files(body=str(os.path.join(f'static/sources/notebooks/{dirname}', filename)), name=form.name.data)
        user.files.append(file)
        db_sess.commit()
        if not os.path.exists(f'static/sources/notebooks/{dirname}'):
            os.makedirs(f'static/sources/notebooks/{dirname}')
        f.save(os.path.join(f'static/sources/notebooks/{dirname}', filename))
        return redirect('/')
    return render_template('index.html', **param)

@app.route('/notebook<notebook_id>', methods=['GET', 'POST'])
def notebook(notebook_id):
    global path
    db_sess = db_session.create_session()
    file = db_sess.query(Files).filter(Files.user_id == current_user.id)[int(notebook_id)]
    path = file.body
    if not current_user.is_authenticated:
        return redirect('/login')
    param = {}

    form = FileuploadForm()

    param['bootstrap'] = url_for('static', filename='css/bootstrap.min.css')
    param['style'] = url_for('static', filename='css/style.css')
    param['clouds'] = url_for('static', filename='sources/icons/clouds.svg')
    param['circle'] = url_for('static', filename='sources/icons/person-circle.svg')
    param['arrow_left'] = url_for('static', filename='sources/icons/arrow-left.svg')
    param['arrow_right'] = url_for('static', filename='sources/icons/arrow-right.svg')
    param['download'] = url_for('static', filename='sources/icons/download.svg')
    param['username'] = current_user.name
    param['pdfviewer'] = url_for('static', filename='scripts/pdfviewer.js')
    param['form'] = form

    if request.method == 'POST':
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        path = connect_pdf("/".join(user.files[int(notebook_id)].body.split("/")[:-1]) + "/")
        cache = io.BytesIO()
        with open(path, 'rb') as fp:
            shutil.copyfileobj(fp, cache)
            cache.flush()
        cache.seek(0)
        os.remove(path)
        return send_file(cache, as_attachment=True, download_name="all_in_one.pdf")

    return render_template('notebook.html', **param)


@app.route('/lecture<lecture_id>')
def lecture(lecture_id):
    global path
    db_sess = db_session.create_session()
    file = db_sess.query(Files).filter(Files.user_id == current_user.id)[int(lecture_id)]
    path = file.body
    if not current_user.is_authenticated:
        return redirect('/login')
    param = {}
    param['bootstrap'] = url_for('static', filename='css/bootstrap.min.css')
    param['style'] = url_for('static', filename='css/style.css')
    param['clouds'] = url_for('static', filename='sources/icons/clouds.svg')
    param['circle'] = url_for('static', filename='sources/icons/person-circle.svg')
    param['arrow_left'] = url_for('static', filename='sources/icons/arrow-left.svg')
    param['arrow_right'] = url_for('static', filename='sources/icons/arrow-right.svg')
    param['download'] = url_for('static', filename='sources/icons/download.svg')
    param['username'] = current_user.name
    param['pdfviewer'] = url_for('static', filename='scripts/pdfviewer.js')
    return render_template('lecture.html', **param)


@app.route('/json')
def json():
    global path
    data = {
        'key1': path,
    }
    return jsonify(data)


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


@app.route('/profile')
def profile():
    if not current_user.is_authenticated:
        return redirect('/login')
    param = {}
    param['bootstrap'] = url_for('static', filename='css/bootstrap.min.css')
    param['style'] = url_for('static', filename='css/style.css')
    param['clouds'] = url_for('static', filename='sources/icons/clouds.svg')
    param['username'] = current_user.name
    param['email'] = current_user.email
    return render_template('profile.html', **param)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/changepass', methods=['POST', 'GET'])
@login_required
def changepass():
    form = ChangepassForm()
    param = {}
    param['bootstrap'] = url_for('static', filename='css/bootstrap.min.css')
    param['style'] = url_for('static', filename='css/style.css')
    param['clouds'] = url_for('static', filename='sources/icons/clouds.svg')
    param['form'] = form
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            param['message'] = 'Пароли не совпадают'
            return render_template('changepass.html', **param)
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == current_user.email).first()
        user.set_password(form.password.data)
        db_sess.commit()
        return redirect('/profile')
    return render_template('changepass.html', **param)


@app.route('/download-notebook')
@login_required
def doenload_notebook():
    return redirect("/")


@app.route('/delete-notebook')
@login_required
def delete_notebook():
    return redirect("/")


if __name__ == '__main__':
    db_session.global_init("db/users.db")
    app.run(port=8080, host='127.0.0.1')