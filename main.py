from flask import Flask, request, url_for, render_template, redirect, session, jsonify, send_file
from data import db_session
from data.users import User
from data.files import Files
from forms.signinform import SigninForm
from forms.loginform import LoginForm
from forms.changepassform import ChangepassForm
from forms.fileuploadform import FileuploadForm
from forms.lectureuploadform import LectureuploadForm
from pdfedit import connect_pdf
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os, shutil

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
    param = {
        'bootstrap': url_for('static', filename='css/bootstrap.min.css'),
        'style': url_for('static', filename='css/style.css'),
        'bootstrap_js': url_for('static', filename='scripts/bootstrap.bundle.min.js'),
        'plus': url_for('static', filename='sources/icons/plus.svg'),
        'doc': url_for('static', filename='sources/icons/doc.svg'),
        'three_dots': url_for('static', filename='sources/icons/three-dots-vertical.svg'),
        'clouds': url_for('static', filename='sources/icons/clouds.svg'),
        'circle': url_for('static', filename='sources/icons/person-circle.svg'),
        'authorized': current_user.is_authenticated,
        'form': form,
        'notebooks': [],
    }
    if current_user.is_authenticated:
        param['username'] = current_user.name
        param['notebooks'] = current_user.files
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        f = form.file.data
        filename = secure_filename(f.filename)
        dirname = current_user.name + "_" + form.name.data
        filename = form.name.data + '_00'
        file = Files(body=str(os.path.join(f'static/sources/notebooks/{dirname}', filename)), name=form.name.data)
        user.files.append(file)
        db_sess.commit()
        if not os.path.exists(f'static/sources/notebooks/{dirname}'):
            os.makedirs(f'static/sources/notebooks/{dirname}')
        path = os.path.join(f'static/sources/notebooks/{dirname}', filename)
        f.save(path)
        shutil.copy(path, path[:-1] + '1')
        return redirect('/')
    return render_template('index.html', **param)

@app.route('/notebook<int:notebook_id>', methods=['GET', 'POST'])
def notebook(notebook_id):
    if not current_user.is_authenticated:
        return redirect('/login')
    global path
    db_sess = db_session.create_session()
    file = db_sess.query(Files).filter(Files.id == notebook_id).first()
    path = file.body
    form = LectureuploadForm()
    param = {
        'bootstrap': url_for('static', filename='css/bootstrap.min.css'),
        'style': url_for('static', filename='css/style.css'),
        'clouds': url_for('static', filename='sources/icons/clouds.svg'),
        'circle': url_for('static', filename='sources/icons/person-circle.svg'),
        'arrow_left': url_for('static', filename='sources/icons/arrow-left.svg'),
        'arrow_right': url_for('static', filename='sources/icons/arrow-right.svg'),
        'download': url_for('static', filename='sources/icons/download.svg'),
        'trash': url_for('static', filename='sources/icons/trash.svg'),
        'username': current_user.name,
        'pdfviewer': url_for('static', filename='scripts/pdfviewer.js'),
        'form': form,
        'lect_num': file.lect_num + 1,
        'notebook_id': file.id,
        'notebook_name': file.name,
    }
    if form.validate_on_submit():
        f = form.file.data
        postfix = str(file.lect_num + 1) if file.lect_num > 9 else '0' + str(file.lect_num + 1)
        filename = path[:-2] + postfix
        file.lect_num = file.lect_num + 1
        db_sess.commit()
        f.save(filename)
        return redirect(f'/notebook{notebook_id}')
    return render_template('notebook.html', **param)


@app.route('/lecture<int:notebook_id>-<int:lecture_id>')
def lecture(notebook_id, lecture_id):
    global path
    if not current_user.is_authenticated:
        return redirect('/login')
    db_sess = db_session.create_session()
    file = db_sess.query(Files).filter(Files.id == notebook_id).first()
    postfix = str(lecture_id) if lecture_id > 9 else '0' + str(lecture_id)
    path = file.body[:-2] + postfix
    param = {
        'bootstrap': url_for('static', filename='css/bootstrap.min.css'),
        'style': url_for('static', filename='css/style.css'),
        'clouds': url_for('static', filename='sources/icons/clouds.svg'),
        'circle': url_for('static', filename='sources/icons/person-circle.svg'),
        'arrow_left': url_for('static', filename='sources/icons/arrow-left.svg'),
        'arrow_right': url_for('static', filename='sources/icons/arrow-right.svg'),
        'download': url_for('static', filename='sources/icons/download.svg'),
        'trash': url_for('static', filename='sources/icons/trash.svg'),
        'username': current_user.name,
        'pdfviewer': url_for('static', filename='scripts/pdfviewer.js'),
        'lect_num': file.lect_num + 1,
        'notebook_id': file.id,
        'lecture_id': lecture_id,
    }
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
    param = {
        'bootstrap': url_for('static', filename='css/bootstrap.min.css'),
        'style': url_for('static', filename='css/style.css'),
        'clouds': url_for('static', filename='sources/icons/clouds.svg'),
        'form': form,
    }
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
    param = {
        'bootstrap': url_for('static', filename='css/bootstrap.min.css'),
        'style': url_for('static', filename='css/style.css'),
        'clouds': url_for('static', filename='sources/icons/clouds.svg'),
        'form': form,
    }
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
    param = {
        'bootstrap': url_for('static', filename='css/bootstrap.min.css'),
        'style': url_for('static', filename='css/style.css'),
        'clouds': url_for('static', filename='sources/icons/clouds.svg'),
        'username': current_user.name,
        'email': current_user.email,
    }
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
    param = {
        'bootstrap': url_for('static', filename='css/bootstrap.min.css'),
        'style': url_for('static', filename='css/style.css'),
        'clouds': url_for('static', filename='sources/icons/clouds.svg'),
        'form': form,
    }
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


@app.route('/download-lecture<int:notebook_id>-<int:lecture_id>')
@login_required
def download_lecture(notebook_id, lecture_id):
    db_sess = db_session.create_session()
    file = db_sess.query(Files).filter(Files.id == notebook_id).first()
    postfix = str(lecture_id) if lecture_id > 9 else '0' + str(lecture_id)
    path = file.body[:-2] + postfix

    return send_file(path, as_attachment=True)


@app.route('/download-notebook<notebook_id>')
@login_required
def download_notebook(notebook_id):
    print(notebook_id)
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    path = ''
    for i in user.files:
        if i.id == int(notebook_id):
            path = i.body
            break
    return send_file(path, as_attachment=True)


@app.route('/delete-notebook<notebook_id>')
@login_required
def delete_notebook(notebook_id):
    db_sess = db_session.create_session()
    files = db_sess.query(Files).filter(Files.id == notebook_id, User.id == current_user.id).first()
    if files:
        db_sess.delete(files)
        db_sess.commit()
    return redirect('/')


@app.route("/page_num", methods=["POST", "GET"])
@login_required
def page_num():
    global page_number
    data = request.get_json()
    page_number = int(data['key1'])
    return jsonify({'message': 'success'})



if __name__ == '__main__':
    db_session.global_init("db/users.db")
    app.run(port=8080, host='127.0.0.1')