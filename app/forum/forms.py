# -*- coding:utf-8 -*-
from flask_wtf import Form
from wtforms import StringField, SelectField, SubmitField, TextAreaField
from wtforms.validators import Length, DataRequired, Regexp
from flask_pagedown.fields import PageDownField


class PostForm(Form):
    title = StringField('Title', validators=[Length(1, 200, message="Length wrror, 1~200"), DataRequired(message="Title is none")])
    label = SelectField('Label', validators=[DataRequired(message='label is none')],
                        choices=[('pc', 'PC'),
                                       ('xbox', 'XBOX'),
                                       ('ps4', 'PS4'),
                                       ('iphone', 'iPhone'),
                                       ('android', "Android"),
                                 ("other", "Other")], default='pc')
    content = PageDownField('Content', validators=[DataRequired(message='内容是必须的')])
    submit = SubmitField('Post')


class ReplyForm(Form):
    content = TextAreaField("Add new reply", validators=[DataRequired(message="必须要有内容")])
    submit = SubmitField("Reply")
