from app import app, db
from flask import send_from_directory, render_template, url_for, flash, redirect, request
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from datetime import datetime
import os

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/')
@app.route('/index/')
def index():
    return render_template('index.html', title='Home')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Login Page', form=form)

@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>/')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    fullfilename = os.listdir(os.path.join(app.config['UPLOAD_FOLDER'] + current_user.username))
    path_pic = os.path.join(app.config['PATH_IMAGE'] + current_user.username)
    return render_template('user.html', title='Profile', user=user, user_image = fullfilename, path_pic = path_pic)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username, current_user.email)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.bio = form.bio.data
        current_user.firstname = form.firstname.data
        current_user.age = form.age.data
        current_user.email = form.email.data
        current_user.sexpref = form.sexpref.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.bio.data = current_user.bio
        form.firstname.data = current_user.firstname
        form.age.data = current_user.age
        form.email.data = current_user.email
        form.sexpref.data = current_user.sexpref
    return render_template('edit_profile.html', title='Edit Profile', form=form)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload/', methods=['GET', 'POST'])
def upload():
    # form = UploadForm
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):

            if not os.path.exists(app.config['UPLOAD_FOLDER'] + current_user.username):
                os.mkdir(app.config['UPLOAD_FOLDER'] + current_user.username)
            if (len([name for name in os.listdir(app.config['UPLOAD_FOLDER'] + current_user.username)]) <= 5):
            # if (len([name for name in os.listdir(app.config['UPLOAD_FOLDER'] + current_user.username) if os.path.isfile(name)]) <= 5):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'] + current_user.username, filename))
                return redirect(url_for('uploaded_file', filename=filename))
            else:
                flash('You can only have 5 pictures, please delete one of your other picture')
                return redirect(url_for('user', username=current_user.username))

    user = User.query.filter_by(username=current_user.username).first_or_404()
    fullfilename = os.listdir(os.path.join(app.config['UPLOAD_FOLDER'] + current_user.username))
    path_pic = os.path.join(app.config['PATH_IMAGE'] + current_user.username)
    return render_template('upload.html', title='Upload', user=user, user_image = fullfilename, path_pic = path_pic)
    # return render_template('upload.html', title='Upload', form=form)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    flash('Your Picture has been uploaded successfully')
    return redirect(url_for('user', username=current_user.username))
    # return send_from_directory(app.config['UPLOAD_FOLDER'], filename)