# -*- coding:utf-8 -*-
from flask_wtf import Form
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, PasswordField, TextAreaField, RadioField, SubmitField, BooleanField
from wtforms.validators import (Length, DataRequired, InputRequired, Email, EqualTo, ValidationError, URL)
from .models import Member


class SignupForm(Form):
    email = StringField("邮箱", validators=[DataRequired(message="A E-Mail Address is required."),
                                          Email(message="Invalid E-Mail Address")])
    username = StringField('用户名', validators=[DataRequired(message='A Username is required.'), Length(1, 64)])
    password = PasswordField('密码',
                             validators=[InputRequired(), EqualTo('confirm_password', message="Password must match.")])
    confirm_password = PasswordField('确认密码')
    submit = SubmitField('注册')

    def validate_username(self, field):
        user = Member.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError("用户名已被使用")

    def validate_email(self, field):
        email = Member.query.filter_by(email=field.data).first()
        if email:
            raise ValidationError('邮箱已经注册')

    def save(self):
        user = Member(emai=self.email.data,
                      username=self.username.data,
                      password=self.password.data)
        return user.save()


class LoginForm(Form):
    email = StringField('账号', validators=[DataRequired(message="还没有填写邮箱")])
    password = PasswordField('密码', validators=[DataRequired(message='还没有填写密码')])
    remeber_me = BooleanField('记住', default=False)
    submit = SubmitField('登录')


class SettingForm(Form):
    avatar = StringField('新头像上传')
    gender = RadioField('性别',
                        choices=[('genderless', 'genderless'), ('mars', 'mars'), ('venus', 'venus')],)
    signature = TextAreaField('个性签名')
    submit = SubmitField('保存')


class ResetpwForm(Form):
    password = PasswordField("新密码", validators=[InputRequired(), EqualTo('confirm_password', message="Password must match.")])
    confirm_password = PasswordField('确认密码')
    submit = SubmitField("确定")
