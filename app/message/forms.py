# -*- coding:utf-8 -*-
from flask_wtf import Form
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired


class LetterForm(Form):
    content = TextAreaField("Content", validators=[DataRequired()])

