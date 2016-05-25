# -*- coding:utf-8 -*-
from flask_wtf import Form
from wtforms import StringField, TextAreaField


class Game_news(Form):
    title = StringField("标题")
    sentence = StringField("展示语")
    content = TextAreaField("内容")
    pic = StringField("展示图")


class GnewsReplyForm(Form):
    content = TextAreaField("评论")
