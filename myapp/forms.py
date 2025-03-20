from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from myapp.models import User
from myapp import db


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


    def validate_username(self, username):  # custom validation to check if username already exist in database                                          
        user = db.session.execute(db.select(User).where(User.username == username.data)).scalar()
        if user:
            raise ValidationError(message="Username is already taken. Choose a different one.")


    def validate_email(self, email):  # custom validation to check if email already exist in database                                          
        user = db.session.execute(db.select(User).where(User.email == email.data)).scalar()
        if user:
            raise ValidationError(message="Email is already taken. Please choose a different one.")


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Pic', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')


    def validate_username(self, username):   
        if username.data != current_user.username:  # only update if current and updated username are not same
            user = db.session.execute(db.select(User).where(User.username == username.data)).scalar()
            if user:
                raise ValidationError(message="Username is already taken. Choose a different one.")


    def validate_email(self, email): 
        if email.data != current_user.email:    
            user = db.session.execute(db.select(User).where(User.email == email.data)).scalar()
            if user:
                raise ValidationError(message="Email is already taken. Please choose a different one.")