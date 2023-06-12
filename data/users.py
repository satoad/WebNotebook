"""Описание класса пользователя"""

import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(SqlAlchemyBase, UserMixin):
    """Класс пользователя для хранения в бд"""

    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    files = sqlalchemy.orm.relationship("Files", back_populates='user')

    def set_password(self, password):
        """
        Хэширует и схраняет пароль

        :param password: (str) введённый пользователем при регистрации пароль.
        """
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        """
        Сравнивает пароли

        :param password: (str) введённый пользователем при входе пароль.
        :return: (bool) совпадают пароли или нет.
        """
        return check_password_hash(self.hashed_password, password)
