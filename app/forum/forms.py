# -*- coding:utf-8 -*-
from flask_wtf import Form
from wtforms import StringField, SelectField, SubmitField, TextAreaField
from wtforms.validators import Length, DataRequired, Regexp
from flask_pagedown.fields import PageDownField


class PostForm(Form):
    title = StringField('标题', validators=[Length(1, 200, message="长度不符合要求"), DataRequired(message='标题是必须的')])
    label = SelectField('标签', validators=[DataRequired(message='标签是必须的')],
                        choices=[('国语', '国语'),
                                       ('欧美', '欧美'),
                                       ('日韩', '日韩'),
                                       ('纯音乐', '纯音乐'),
                                       ('其它', '其它')], default='国语')
    music_chain = StringField('音乐iframe', validators=[DataRequired(message='音乐iframe是必须的'), Regexp(r"^<iframe.*?</iframe>$", message="格式不正确")])
    content = PageDownField('内容', validators=[DataRequired(message='内容是必须的')])
    submit = SubmitField('发布')


class ReplyForm(Form):
    content = TextAreaField("添加一条新回复", validators=[DataRequired(message="必须要有内容")])
    submit = SubmitField("回复")
