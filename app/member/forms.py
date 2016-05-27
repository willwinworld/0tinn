# -*- coding:utf-8 -*-
from flask_wtf import Form
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, PasswordField, TextAreaField, RadioField, SubmitField, BooleanField
from wtforms.validators import (Length, DataRequired, InputRequired, Email, EqualTo, ValidationError, URL)
from .models import Member


class SignupForm(Form):
    email = StringField("Email", validators=[DataRequired(message="A E-Mail Address is required."),
                                          Email(message="Invalid E-Mail Address")])
    username = StringField('Username', validators=[DataRequired(message='A Username is required.'), Length(1, 64)])
    password = PasswordField('Password',
                             validators=[InputRequired(), EqualTo('confirm_password', message="Password must match.")])
    confirm_password = PasswordField('Confirm password')
    submit = SubmitField('Sign up')

    def validate_username(self, field):
        user = Member.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError("Username is already in use")

    def validate_email(self, field):
        email = Member.query.filter_by(email=field.data).first()
        if email:
            raise ValidationError('E-mail is already registered')

    def save(self):
        user = Member(emai=self.email.data,
                      username=self.username.data,
                      password=self.password.data)
        return user.save()


class LoginForm(Form):
    email = StringField('Username', validators=[DataRequired(message="还没有填写邮箱")])
    password = PasswordField('Password', validators=[DataRequired(message='还没有填写密码')])
    remeber_me = BooleanField('Remeber', default=False)
    submit = SubmitField('Sign in')


class SettingForm(Form):
    avatar = StringField('Upload new avatar')
    gender = RadioField('Gender',
                        choices=[('genderless', 'genderless'), ('mars', 'mars'), ('venus', 'venus')],)
    signature = TextAreaField('Signature')
    submit = SubmitField('Submit')


class ResetpwForm(Form):
    password = PasswordField("New password", validators=[InputRequired(), EqualTo('confirm_password', message="Password must match.")])
    confirm_password = PasswordField('Confirm password')
    submit = SubmitField("Confirm")
