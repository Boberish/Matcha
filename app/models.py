from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    firstname = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    age = db.Column(db.Integer, index=True)
    sexpref = db.Column(db.String(64), index=True)
    fame = db.Column(db.Integer, index=True)
    bio = db.Column(db.String(256), index=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User {} {} {}>'.format(self.username, self.firstname, self.email)
