"""Тесты"""

import unittest
from webnotebook.data.files import Files
from webnotebook.data.users import User
from webnotebook.data import db_session
from webnotebook.pdfedit import connect_pdf, add_page, page_delete
import PyPDF2


class UserModelCase(unittest.TestCase):
    """Тесты"""

    db_session.global_init("webnotebook/db/users.db")
    db_sess = db_session.create_session()

    def test_1(self):
        """Тест хэширования пароля"""
        u = User(name='susan', email='susan@example.com')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_2(self):
        """Тест таблицы пользователей"""
        u1 = User(name='john', email='lol@example.com')
        u1.set_password('cat')
        u2 = User(name='susan', email='kek@example.com')
        u2.set_password('dog')

        self.db_sess.add(u1)
        self.db_sess.add(u2)
        self.db_sess.commit()
        self.assertEqual(u1.id, 1)
        self.assertEqual(u2.id, 2)

        u3 = User(name='alex', email='alex@example.com')
        u3.set_password('bird')

        self.db_sess.add(u3)
        self.db_sess.commit()
        self.assertEqual(u3.id, 3)

        for i in range(1, 4):
            user = self.db_sess.query(User).filter(User.id == i).first()
            if user:
                self.db_sess.delete(user)
                self.db_sess.commit()

    def test_3(self):
        """Тест таблицы файлов"""
        u1 = User(name='john', email='john@example.com')
        u1.set_password('cat')
        u2 = User(name='susan', email='susan@example.com')
        u2.set_password('dog')
        u3 = User(name='alex', email='alex@example.com')
        u3.set_password('bird')
        self.db_sess.add_all([u1, u2, u3])
        self.db_sess.commit()

        p1 = Files(body="/example/of/the/way1/", name='1')
        user = self.db_sess.query(User).filter(User.id == u1.id).first()
        user.files.append(p1)
        self.db_sess.commit()

        p2 = Files(body="/example/of/the/way2/", name='1')
        user = self.db_sess.query(User).filter(User.id == u2.id).first()
        user.files.append(p2)
        self.db_sess.commit()

        p3 = Files(body="/example/of/the/way3/", name='1')
        user = self.db_sess.query(User).filter(User.id == u3.id).first()
        user.files.append(p3)
        self.db_sess.commit()

        self.assertEqual(p1.id, 1)
        self.assertEqual(p2.id, 2)
        self.assertEqual(p3.id, 3)

        for i in range(1, 4):
            files = self.db_sess.query(Files).filter(Files.id == i).first()
            if files:
                self.db_sess.delete(files)
                self.db_sess.commit()
            user = self.db_sess.query(User).filter(User.id == i).first()
            if user:
                self.db_sess.delete(user)
                self.db_sess.commit()

    def test_4(self):
        """Тест функции склеивания пдф"""
        path = "webnotebook/static/sources/pdf_test"
        self.assertEqual(connect_pdf(path), path + "/test_00.pdf")

        file = open(path + "/test_00.pdf", 'rb')
        readpdf = PyPDF2.PdfReader(file)
        totalpages = len(readpdf.pages)
        file.close()

        sum_of_pages = 0

        file = open(path + "/test_01.pdf", 'rb')
        readpdf = PyPDF2.PdfReader(file)
        sum_of_pages += len(readpdf.pages)
        file.close()

        file = open(path + "/test_02.pdf", 'rb')
        readpdf = PyPDF2.PdfReader(file)
        sum_of_pages += len(readpdf.pages)
        file.close()

        file = open(path + "/test_03.pdf", 'rb')
        readpdf = PyPDF2.PdfReader(file)
        sum_of_pages += len(readpdf.pages)
        file.close()

        self.assertEqual(totalpages, sum_of_pages)

    def test_5(self):
        """Тест функции удаления страницы"""
        path = "webnotebook/static/sources/pdf_test/test_03.pdf"
        file = open(path, 'rb')
        readpdf = PyPDF2.PdfReader(file)
        totalpages_before = len(readpdf.pages)
        file.close()

        page_delete(path, 1)

        file = open(path, 'rb')
        readpdf = PyPDF2.PdfReader(file)
        totalpages_after = len(readpdf.pages)
        file.close()

        self.assertEqual(totalpages_before - 1, totalpages_after)

    def test_6(self):
        """Тест функции добавления страницы"""
        path_to_pdf = "webnotebook/static/sources/pdf_test/test_03.pdf"

        file = open(path_to_pdf, 'rb')
        readpdf = PyPDF2.PdfReader(file)
        totalpages_before = len(readpdf.pages)
        file.close()

        path_to_pic = "webnotebook/static/sources/pic_test/boot.png"
        add_page(path_to_pdf, path_to_pic, 1)

        file = open(path_to_pdf, 'rb')
        readpdf = PyPDF2.PdfReader(file)
        totalpages_after = len(readpdf.pages)
        file.close()

        self.assertEqual(totalpages_before + 1, totalpages_after)


if __name__ == '__main__':
    unittest.main(verbosity=2)
