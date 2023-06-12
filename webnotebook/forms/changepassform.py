"""Форма для смены пароля"""

from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired


class ChangepassForm(FlaskForm):
    """Форма для смены пароля"""

    password = PasswordField('Новый пароль', validators=[DataRequired()])
    password_again = PasswordField('Подтвердите новый пароль', validators=[DataRequired()])
    submit = SubmitField('Сменить')
