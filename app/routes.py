from app import app, db
from flask import send_from_directory, render_template, url_for, flash, redirect, request
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ResetPasswordRequestForm, ResetPasswordForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from app.email import send_password_reset_email
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
        user.init_profile_pic()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>/')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    fullfilename = os.listdir(os.path.join(app.config['UPLOAD_FOLDER'] + username))
    for file in fullfilename:
        if file == 'profile_pic':
            fullfilename.remove(file)

    profile_pic = user.profile_pic()
    path_pic = app.config['PATH_IMAGE'] + username
    return render_template('user.html', title='Profile', user=user, user_image = fullfilename, path_pic = path_pic, profile_pic=profile_pic)


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
        path = app.config['UPLOAD_FOLDER'] + current_user.username + '/profile_pic/'

        if file and allowed_file(file.filename):
            if (len([name for name in os.listdir(app.config['UPLOAD_FOLDER'] + current_user.username)]) <= 5):
                filename = secure_filename(file.filename)
                if not os.listdir(path):
                    file.save(os.path.join(path, filename))
                else:
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'] + current_user.username, filename))
                return redirect(url_for('uploaded_file', filename=filename))
            else:
                flash('You can only have 5 pictures, please delete one of your other picture')
                return redirect(url_for('user', username=current_user.username))

    user = User.query.filter_by(username=current_user.username).first_or_404()
    user_image = current_user.get_img_paths()
    return render_template('upload.html', title='Upload', user=user, user_image=user_image)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    flash('Your Picture has been uploaded successfully')
    return redirect(url_for('user', username=current_user.username))

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/explore/')
@login_required
def explore():
    # A changer pour le mettre dynamiquement: all the user the current_user doen't like and didn't block
    profile_list = User.query.all()
    print(profile_list)
    # fin du changement

    return render_template('explore.html', title='Explore', profile_list=profile_list)

@app.route('/likes/')
@login_required
def likes_page():
    profiles_you_like = current_user.your_likes()
    profiles_who_liked_you = current_user.likes_you()
    print("====>  ***profiles_you_like {}".format(profiles_you_like))
    return render_template('likes_page.html', title='Your Likes', profiles_you_like=profiles_you_like, profiles_who_liked_you=profiles_who_liked_you)

@app.route('/matches/')
@login_required
def matches_page():
    # to change for the function who doesn't exist yet
    profiles_matches = current_user.your_likes()
    print("====>  ***profiles_matches {}".format(profiles_matches))
    return render_template('matches_page.html', title='Matches', profiles_matches=profiles_matches)

@app.route('/like/<username>')
@login_required
def like(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot like yourself!')
        return redirect(url_for('user', username=username))
    current_user.add_like(user)
    db.session.commit()
    flash('You now like {}!'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/unlike/<username>')
@login_required
def unlike(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.del_like(user)
    db.session.commit()
    flash('You unliked {}.'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/swap_prof_pic/')
def swap_prof_pic():
    picture = request.args.get('type')
    print(os.getcwd())
    print("picture:  {}".format(picture))

    picture = picture.rsplit('/',1)
    print("AFTERKDKDKDKK----------------{}".format(picture))
    oldProPic = os.listdir('app/' + picture[0]  + '/profile_pic/')
    os.rename('app/' + picture[0]  + '/profile_pic/' + oldProPic[0], 'app/' + picture[0] + '/' + oldProPic[0])
    os.rename('app/' + picture[0] + '/' + picture[1], 'app/' + picture[0]  + '/profile_pic/' + picture[1])
    
    flash('Your Profile picture has been updated')
    return redirect(url_for('user', username=current_user.username))

 