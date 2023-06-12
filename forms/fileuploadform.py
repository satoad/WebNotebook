"""Форма для загрузки тетрадей на сервер"""

from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from flask_wtf.file import FileRequired, FileField
from wtforms.validators import DataRequired


class FileuploadForm(FlaskForm):
    """Форма для загрузки тетрадей на сервер"""

    file = FileField('Загрузить', validators=[FileRequired()])
    name = StringField('Название тетради', validators=[DataRequired()])
    submit = SubmitField('Загрузить')
