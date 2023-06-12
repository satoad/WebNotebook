"""Форма для входа"""

from flask_wtf import FlaskForm
from wtforms import PasswordField, EmailField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    """Форма для входа"""

    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')
