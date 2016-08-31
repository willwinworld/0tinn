# -*- coding:utf-8 -*-
from flask import Blueprint, render_template, session
from flask_login import current_user
from app.forum.models import Topic
from app.message.models import Message
from app.game.models import Game_News
from app.util.helper import get_online_user_nums, highest_online_number
index = Blueprint("index", __name__)


@index.route('/', methods=['GET'])
def main():
    hot_news = Game_News.get_hot()
    news_index = Game_News.get_index()
    news = Game_News.get(1).items
    for n in news:
        p = n.pic.split('.')
        p[-2] += 'm'
        n.pic = '.'.join(p)
    if current_user.is_authenticated:
        session['my_topic_num'] = Topic.get_user_topic_num(username=current_user.username)
        session['msg_num'] = Message.get_user_unread_num(current_user.id)
        session['following_nums'] = current_user.following_num
    session['online_nums'] = get_online_user_nums()
    session["highest_online_num"] = highest_online_number()
    return render_template("index.html", hot_news=hot_news, news_index=news_index, news=news)
