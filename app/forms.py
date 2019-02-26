from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField, RadioField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, NumberRange, Optional
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    firstname = StringField('Firstname', validators=[DataRequired()])
    bio = TextAreaField('About me', validators=[Length(min=0, max=256)])
    age = IntegerField('Age', validators=[NumberRange(min=18, max=100), DataRequired()])
    sexpref = RadioField('Sexual Preference', choices = [("Male ","Male"), ("Female", "Female"), ("Both", "Both")], validators=[DataRequired()])
    email = StringField('Update your Email', validators=[Email(), DataRequired()])
    
    submit = SubmitField('Submit')

    # username = StringField('Username', validators=[Optional()])
    # firstname = StringField('Firstname', validators=[Optional()])
    # bio = TextAreaField('About me', validators=[Length(min=0, max=256)])
    # age = IntegerField('Age', validators=[NumberRange(min=18, max=100), Optional()])
    # sexpref = RadioField('Sexual Preference', choices = [("Male ","Male"), ("Female", "Female"), ("Both", "Both")], validators=[Optional()])
    # email = StringField('Update your Email', validators=[Email(), Optional()])
    # submit = SubmitField('Submit')

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')
    
    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=self.email.data).first()
            if user is not None:
                raise ValidationError('Please use a different email.')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')





