from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, jsonify, current_app
from flask_login import current_user, login_required
from app import db
from app.main.forms import EditProfileForm
from app.models import User
from app.main import bp
import os
from werkzeug.utils import secure_filename


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@bp.route('/')
@bp.route('/index/')
def index():
    return render_template('index.html', title='Home')

@bp.route('/explore')
@login_required
def explore():
    # A changer pour le mettre dynamiquement: all the user the current_user doen't like and didn't block
    profile_list = User.query.all()
    for profile in profile_list:
        if profile == current_user:
            profile_list.remove(profile)
    # print(profile_list)
    # fin du changement

    return render_template('explore.html', title='Explore', profile_list=profile_list)

@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    current_user.add_look(user)
    user_pics = user.get_user_img_paths()
    profile_pic = user.profile_pic()
    history = current_user.get_your_looks()
    looked_at_you = current_user.get_looked_at_you()
    return render_template('user.html', title='Profile',looked_at_you=looked_at_you, user=user, user_pics = user_pics, profile_pic=profile_pic, history=history)


@bp.route('/edit_profile', methods=['GET', 'POST'])
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
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.bio.data = current_user.bio
        form.firstname.data = current_user.firstname
        form.age.data = current_user.age
        form.email.data = current_user.email
        form.sexpref.data = current_user.sexpref
    user_image = current_user.get_img_paths()
    return render_template('edit_profile.html', title='Edit Profile', form=form, user_image=user_image)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@bp.route('/upload/', methods=['GET', 'POST'])
@login_required
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
        path = current_app.config['UPLOAD_FOLDER'] + current_user.username + '/profile_pic/'

        if file and allowed_file(file.filename):
            if (len([name for name in os.listdir(current_app.config['UPLOAD_FOLDER'] + current_user.username)]) <= 5):
                filename = secure_filename(file.filename)
                if not os.listdir(path):
                    file.save(os.path.join(path, filename))
                else:
                    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'] + current_user.username, filename))
                return redirect(url_for('main.uploaded_file', filename=filename))
            else:
                flash('You can only have 5 pictures, please delete one of your other picture')
                return redirect(url_for('main.user', username=current_user.username))

    user = User.query.filter_by(username=current_user.username).first_or_404()
    user_image = current_user.get_img_paths()
    return render_template('upload.html', title='Upload', user=user, user_image=user_image)

@bp.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    flash('Your Picture has been uploaded successfully')
    return redirect(url_for('main.user', username=current_user.username))

@bp.route('/likes/')
@login_required
def likes_page():
    profiles_you_like = current_user.your_likes()
    profiles_who_liked_you = current_user.likes_you()
    # print("====>  ***profiles_you_like {}".format(profiles_you_like))
    return render_template('likes_page.html', title='Your Likes', profiles_you_like=profiles_you_like, profiles_who_liked_you=profiles_who_liked_you)

@bp.route('/matches/')
@login_required
def matches_page():
    # to change for the function who doesn't exist yet
    profiles_matches = current_user.your_likes()
    # print("====>  ***profiles_matches {}".format(profiles_matches))
    return render_template('matches_page.html', title='Matches', profiles_matches=profiles_matches)

@bp.route('/like/<username>')
@login_required
def like(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot like yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.add_like(user)
    db.session.commit()
    flash('You now like {}!'.format(username))
    return redirect(url_for('main.user', username=username))

@bp.route('/unlike/<username>')
@login_required
def unlike(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.del_like(user)
    db.session.commit()
    flash('You unliked {}.'.format(username))
    return redirect(url_for('main.user', username=username))

@bp.route('/swap_prof_pic/')
@login_required
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
    return redirect(url_for('main.user', username=current_user.username))

# @bp.route('/test/')
# def test():
#     # Retrieve geoip data for the given requester
#     simple_geoip = SimpleGeoIP(app)
#     geoip_data = simple_geoip.get_geoip_data()
#     # print jsonify(data=geoip_data)
#     resultOfApi = jsonify(data=geoip_data)
#     print("------> resultOfApi: ", geoip_data)
#     print(resultOfApi)
#     return jsonify(data=geoip_data)
#     # return render_template('test.html', title='Te