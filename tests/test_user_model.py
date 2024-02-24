import time
import unittest

from app import db
from app.models import User


class UserModelTestCase(unittest.TestCase):
    def test_password_setter(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_valid_confirmation_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))

    def test_invalid_confirmation_token(self):
        u1 = User(password='cat')
        u2 = User(password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))

    def test_expired_confirmation_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        time.sleep(2)
        self.assertFalse(u.confirm(token, 1))

    def test_valid_reset_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertTrue(User.reset_password(token, 'dog'))
        self.assertTrue(u.verify_password('dog'))

    def test_invalid_reset_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertFalse(User.reset_password(token + 'a', 'horse'))
        self.assertTrue(u.verify_password('cat'))

    # User.email具有唯一性，每一次测试都需要删除以前测试用的Email
    def test_valid_email_change_token(self):
        user1 = User.query.filter_by(email='123@qq.com').first()
        user2 = User.query.filter_by(email='1234@qq.com').first()
        if user1:
            db.session.delete(user1)
        if user2:
            db.session.delete(user2)
        db.session.commit()
        u = User(email='123@qq.com', password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_email_change_token('1234@qq.com')
        self.assertTrue(u.change_email(token))
        self.assertTrue(u.email == '1234@qq.com')

    def test_invalid_email_change_token(self):
        user1 = User.query.filter_by(email='234@qq.com').first()
        user2 = User.query.filter_by(email='345@qq.com').first()
        user3 = User.query.filter_by(email='456@qq.com').first()
        if user1:
            db.session.delete(user1)
        if user2:
            db.session.delete(user2)
        if user3:
            db.session.delete(user3)
        db.session.commit()
        u1 = User(email='234@qq.com', password='cat')
        u2 = User(email='345@qq.com', password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_email_change_token('456@qq.com')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == '345@qq.com')

    def test_duplicate_email_change_token(self):
        user1 = User.query.filter_by(email='567@qq.com').first()
        user2 = User.query.filter_by(email='678@qq.com').first()
        if user1:
            db.session.delete(user1)
        if user2:
            db.session.delete(user2)
        db.session.commit()
        u1 = User(email='567@qq.com', password='cat')
        u2 = User(email='678@qq.com', password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u2.generate_email_change_token('567@qq.com')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == '678@qq.com')
