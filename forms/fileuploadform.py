from flask_wtf import FlaskForm
from wtforms import SubmitField
from flask_wtf.file import FileRequired, FileField, FileAllowed


class FileuploadForm(FlaskForm):
    file = FileField('Загрузить', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField('Загрузить')