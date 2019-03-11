from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import url_for, current_app
from flask_login import current_user
from time import time
import jwt
# from app import app
import os

likes = db.Table('likes',db.Column('likes_id', db.Integer, db.ForeignKey('user.id')), 
    db.Column('liked_id', db.Integer, db.ForeignKey('user.id')) )

looks = db.Table('looks',db.Column('looks_id', db.Integer, db.ForeignKey('user.id')), 
    db.Column('looked_id', db.Integer, db.ForeignKey('user.id')) )

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
    # localisation_lat = db.Column(db.Float, index=True)
    # localisation_long = db.Column(db.Float, index=True)
    fame = db.Column(db.Integer, index=True)
    liked = db.relationship(
        'User', secondary=likes,
        primaryjoin=(likes.c.likes_id == id),
        secondaryjoin=(likes.c.liked_id == id),
        backref=db.backref('likes', lazy='dynamic'),lazy='dynamic')
    looked = db.relationship(
        'User', secondary=looks,
        primaryjoin=(looks.c.looks_id == id),
        secondaryjoin=(looks.c.looked_id == id),
        backref=db.backref('looks', lazy='dynamic'),lazy='dynamic'
    )

    def add_look(self, user):
        if self.username != user.username:
            self.looked.append(user)
            db.session.commit()

    def get_your_looks(self):
        return User.query.join(looks, (looks.c.looked_id == User.id)).filter(looks.c.looks_id == self.id).all()

    def get_looked_at_you(self):
        return User.query.join(looks, (looks.c.looks_id == User.id)).filter(looks.c.looked_id == self.id).all()
    
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

    def likes_you(self):
        return User.query.join(likes,(likes.c.likes_id == User.id)).filter(likes.c.liked_id == self.id).all()

    def profile_pic(self):
        path = os.path.join(os.getenv('PATH_IMAGE', '/static/images') , self.username, 'profile_pic/')
        pic = os.listdir('app' + path)
        if not pic:
            return(os.path.join(os.getenv('PATH_IMAGE', '/static/images/'),'default_prof_pic', 'profile_empty.jpeg'))
        return(path + pic[0])
    
    def get_user_img_paths(self):
        filelist = os.listdir(os.path.join(current_app.config['UPLOAD_FOLDER'] + self.username))
        final = [current_app.config['PATH_IMAGE']  + self.username + '/' + file for file in filelist if file != "profile_pic"]
        return final


    def get_liked(self):
        print( '<User likes {}>'.format(self.liked.all()))

    def your_likes(self):
        return User.query.join(likes, (likes.c.liked_id == User.id)).filter(likes.c.likes_id == self.id).all()

    def your_matches(self):
        yl = User.query.join(likes, (likes.c.liked_id == User.id)).filter(likes.c.likes_id == self.id).all()
        lm = User.query.join(likes,(likes.c.likes_id == User.id)).filter(likes.c.liked_id == self.id).all()
        matches = []

        for l in yl:
            if l in lm:
                matches.append(l)

        return matches

    def init_profile_pic(self):
        try:
            os.makedirs('app/static/images/' + self.username + '/profile_pic/')
        except:
            pass

    def get_img_paths(self):
        image_name_list = os.listdir(os.path.join(current_app.config['UPLOAD_FOLDER'] + self.username))
        path = os.path.join(current_app.config['PATH_IMAGE'] , self.username)

        final = [path + '/' + img for img in image_name_list if img != 'profile_pic']
        return(final)

    def __repr__(self):
        return '<User username:{}, firstname:{}, email:{}>'.format(self.username, self.firstname, self.email)
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)




@login.user_loader
def load_user(id):
    return User.query.get(int(id))

