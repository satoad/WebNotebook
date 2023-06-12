"""Основной модуль, запускающий приложение"""

from flask import Flask
from flask import request
from flask import url_for
from flask import render_template
from flask import redirect
from flask import jsonify
from flask import send_file
from data import db_session
from data.users import User
from data.files import Files
from forms.signinform import SigninForm
from forms.loginform import LoginForm
from forms.changepassform import ChangepassForm
from forms.fileuploadform import FileuploadForm
from forms.lectureuploadform import LectureuploadForm
from pdfedit import connect_pdf
from pdfedit import add_page
from pdfedit import page_delete
from flask_login import LoginManager
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from flask_login import current_user
from werkzeug.utils import secure_filename
import os
import shutil
import gettext

app = Flask(__name__, template_folder='templates')
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

popath = os.path.join(os.path.dirname(__file__), 'po')
translation_en = gettext.translation("webnotebook", popath, fallback=True, languages='en')
translation_ru = gettext.translation("webnotebook", popath, fallback=True)
ru = translation_ru.gettext
en = translation_en.gettext
_ = ru


@login_manager.user_loader
def load_user(user_id):
    """Загружает пользователя с user_id из базы данных"""
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    """Реализует работу главной страницы сайта"""
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
        'translate': url_for('static', filename='sources/icons/translate.svg'),
        'notebooks': [],
        'login': _('Login'),
        'my_profile': _('My Profile'),
        'my_notebooks': _('My Notebooks'),
        'open': _('Open'),
        'download': _('Download'),
        'delete': _('Delete'),
        'notebook_name': _('Notebook Name'),
        'upload': _('Upload'),
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
        filename = form.name.data + '_00.pdf'
        file = Files(body=str(os.path.join(f'static/sources/notebooks/{dirname}', filename)), name=form.name.data)
        user.files.append(file)
        db_sess.commit()
        if not os.path.exists(f'static/sources/notebooks/{dirname}'):
            os.makedirs(f'static/sources/notebooks/{dirname}')
        path = os.path.join(f'static/sources/notebooks/{dirname}', filename)
        f.save(path)
        shutil.copy(path, path[:-5] + '1.pdf')
        return redirect('/')
    return render_template('index.html', **param)


@app.route('/notebook<int:notebook_id>', methods=['GET', 'POST'])
def notebook(notebook_id):
    """Страница сайта, отображающая конкретную тетрадь"""
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
        postfix = str(file.lect_num + 1) + '.pdf' if file.lect_num > 9 else '0' + str(file.lect_num + 1) + '.pdf'
        filename = path[:-6] + postfix
        file.lect_num = file.lect_num + 1
        db_sess.commit()
        f.save(filename)
        connect_pdf(os.path.dirname(path))
        return redirect(f'/notebook{notebook_id}')
    return render_template('notebook.html', **param)


@app.route('/lecture<int:notebook_id>-<int:lecture_id>', methods=['POST', 'GET'])
def lecture(notebook_id, lecture_id):
    """Страница сайта, отображающая отдельную лекцию из тетради"""
    global path
    global page_number
    if not current_user.is_authenticated:
        return redirect('/login')
    db_sess = db_session.create_session()
    file = db_sess.query(Files).filter(Files.id == notebook_id).first()
    postfix = str(lecture_id) + '.pdf' if lecture_id > 9 else '0' + str(lecture_id) + '.pdf'
    path = file.body[:-6] + postfix
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
        'lect_num': file.lect_num + 1,
        'notebook_id': file.id,
        'lecture_id': lecture_id,
        'form': form,
    }
    if form.validate_on_submit():
        f = form.file.data
        filename = secure_filename(f.filename)
        filename = os.path.join(os.path.dirname(path), filename)
        f.save(filename)
        add_page(path, filename, page_number)
        return render_template('lecture.html', **param)
    return render_template('lecture.html', **param)


@app.route('/signin', methods=['POST', 'GET'])
def signin():
    """Страница регистрации пользователей"""
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
            return render_template('signin.html', **param)
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
    """Страница входа"""
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
    """Страница профиля"""
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


@app.route('/changepass', methods=['POST', 'GET'])
@login_required
def changepass():
    """Страница смены пароля"""
    form = ChangepassForm()
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


@app.route('/download-notebook<notebook_id>')
@login_required
def download_notebook(notebook_id):
    """
    Действие, загружающее выбранную тетрадь.
    Вызывается на главной странице нажатием на '...' -> 'Скачать' возле желаемой тетради.
    """
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
    """
    Действие, удаляющее выбранную тетрадь.
    Вызывается на главной странице нажатием на '...' -> 'Удалить' возле желаемой тетради.
    """
    db_sess = db_session.create_session()
    files = db_sess.query(Files).filter(Files.id == notebook_id, User.id == current_user.id).first()

    shutil.rmtree("/".join(files.body.split("/")[:-1]))
    if files:
        db_sess.delete(files)
        db_sess.commit()
    return redirect('/')


@app.route('/download-lecture<int:notebook_id>-<int:lecture_id>')
@login_required
def download_lecture(notebook_id, lecture_id):
    """
    Действие, осуществляющее загрузку отдельной лекции.
    Вызывается на странице лекции, которую требуется загрузить.
    """
    db_sess = db_session.create_session()
    file = db_sess.query(Files).filter(Files.id == notebook_id).first()
    postfix = str(lecture_id) + '.pdf' if lecture_id > 9 else '0' + str(lecture_id) + '.pdf'
    path = file.body[:-6] + postfix

    return send_file(path, as_attachment=True)


@app.route('/delete-lecture<int:notebook_id>-<int:lecture_id>')
@login_required
def delete_lecture(notebook_id, lecture_id):
    """
    Действие, удаляющее отдельную лекцию.
    Вызывается на странице лекции или тетради
    нажатием на значёк мусорки рядом с желаемой лекией в списке лекций в боковой панели.
    После удаления лекции отправляет пользователя на страницу тетради.
    """
    db_sess = db_session.create_session()
    file = db_sess.query(Files).filter(Files.id == notebook_id).first()
    postfix = str(lecture_id) + '.pdf' if lecture_id > 9 else '0' + str(lecture_id) + '.pdf'
    path = file.body[:-6] + postfix
    file.lect_num -= 1
    file_template = file.body[:-6]
    db_sess.commit()
    dir_name = "/".join(path.split("/")[:-1])
    os.remove(path)
    files = sorted(os.listdir(dir_name))
    if len(files) > 1:
        for index, file in enumerate(files):
            if file[-6:] != "00.pdf":
                if index < 10:
                    os.rename(os.path.join(dir_name, file), ''.join([file_template, '0', str(index), '.pdf']))
                else:
                    os.rename(os.path.join(dir_name, file), ''.join([file_template, str(index), '.pdf']))
        connect_pdf(dir_name)
        return redirect(f"/notebook{notebook_id}")
    else:
        delete_notebook(notebook_id)
        return redirect('/')


@app.route('/delete-page<int:notebook_id>-<int:lecture_id>', methods=['POST', 'GET'])
@login_required
def delete_page(notebook_id, lecture_id):
    """
    Действие, удаляющее отдельную страницу из лекции.
    Вызывается на странице лекции нажатием на кнопку удалить.
    Удаляется страница открытая в pdfviewer на данный момент.
    """
    global page_number
    db_sess = db_session.create_session()
    file = db_sess.query(Files).filter(Files.id == notebook_id).first()
    postfix = str(lecture_id) + '.pdf' if lecture_id > 9 else '0' + str(lecture_id) + '.pdf'
    path = file.body[:-6] + postfix
    page_delete(path, page_number)

    return redirect(f"/lecture{notebook_id}-{lecture_id}")


@app.route("/page_num", methods=["POST", "GET"])
@login_required
def page_num():
    """
    Действие, принимающее по POST запросу номер страницы, отправленный из JS скрипта на клиенте.
    Присваивает глобальной переменной page_number номер страницы, открытой в pdfviewer у клиента на данный момент.
    """
    global page_number
    data = request.get_json()
    page_number = int(data['key1'])
    print(page_number)
    return jsonify({'message': 'success'})


@app.route('/json')
def json():
    """
    Действие, отправляющее значение глобальной переменной data в JS скрипт на клиенте.
    Данное действие необходимо для передачи пользователю информации о расположении файла, который он хочет видеть.
    """
    global path
    data = {
        'key1': path,
    }
    return jsonify(data)


@app.route('/logout')
@login_required
def logout():
    """Действие, осуществляющее разлогинивание"""
    logout_user()
    return redirect("/")


@app.route('/translate')
def ch_translate():
    """Действие, меняет локаль"""
    global _
    global ru
    global en
    if _ == ru:
        _ = en
    else:
        _ = ru
    return redirect("/")


if __name__ == '__main__':
    db_session.global_init("db/users.db")
    app.run(port=8080, host='127.0.0.1')
