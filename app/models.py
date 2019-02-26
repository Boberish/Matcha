from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import url_for
from flask_login import current_user

likes = db.Table('likes',db.Column('likes_id', db.Integer, db.ForeignKey('user.id')), 
    db.Column('liked_id', db.Integer, db.ForeignKey('user.id')) )

class User(UserMixin, db.Model):
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
    liked = db.relationship(
        'User', secondary=likes,
        primaryjoin=(likes.c.likes_id == id),
        secondaryjoin=(likes.c.liked_id == id),
        backref=db.backref('likes', lazy='dynamic'),lazy='dynamic'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def add_like(self, user):
        if not self.does_like(user):
            self.liked.append(user)
    
    def del_like(self, user):
        if self.does_like(user):
            self.liked.remove(user)
            
    def does_like(self, user):
        return self.liked.filter(likes.c.liked_id == user.id).count() > 0
    
    def profile_pic(self):
        # path = url_for(['UPLOAD_FOLDER'] + current_user.username + 'profile_pic.jpeg')
        # print(path)
        # return path
        return 'https://images.unsplash.com/photo-1497316730643-415fac54a2af?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&w=1000&q=80'
        # return 'app/images/profile_empty.jpeg'

    def __repr__(self):
        return '<User {} {} {}>'.format(self.username, self.firstname, self.email)




@login.user_loader
def load_user(id):
    return User.query.get(int(id))