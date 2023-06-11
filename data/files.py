import sqlalchemy
from .db_session import SqlAlchemyBase


class Files(SqlAlchemyBase):
    __tablename__ = 'files'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    body = sqlalchemy.Column(sqlalchemy.String(140))
    name = sqlalchemy.Column(sqlalchemy.String(30), default='Тетрадь')
    lect_num = sqlalchemy.Column(sqlalchemy.Integer, default=1)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    user = sqlalchemy.orm.relationship('User')

