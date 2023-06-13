"""Форма для загрузки лекций и страниц на сервер"""

from flask_wtf import FlaskForm
from wtforms import SubmitField
from flask_wtf.file import FileRequired, FileField


class LectureuploadForm(FlaskForm):
    """Форма для загрузки лекций и страниц на сервер"""

    file = FileField('Загрузить', validators=[FileRequired()])
    submit = SubmitField('Загрузить')
