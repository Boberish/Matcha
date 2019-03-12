from datetime import datetime, timedelta
import unittest
from app import create_app, db
from app.models import User
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_follow(self):
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.liked.all(), [])
        self.assertEqual(u1.liked.all(), [])

        u1.add_like(u2)
        db.session.commit()
        self.assertTrue(u1.does_like(u2))
        self.assertEqual(u1.liked.count(), 1)
        self.assertEqual(u1.liked.first().username, 'susan')
        self.assertEqual(u2.likes.count(), 1)
        self.assertEqual(u2.likes.first().username, 'john')

        u1.del_like(u2)
        db.session.commit()
        self.assertFalse(u1.does_like(u2))
        self.assertEqual(u1.liked.count(), 0)
        self.assertEqual(u2.likes.count(), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)