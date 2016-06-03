# -*- coding:utf-8 -*-
import json
from flask import Blueprint,render_template, flash, url_for, redirect, session, request, current_app
from flask_login import current_user, login_required
from .models import Topic, Reply
from .forms import PostForm, ReplyForm
from app.message.models import Message

forum = Blueprint('forum', __name__)


@forum.route('/forum', methods=['POST', 'GET'])
def index():
    hot_topics = Topic.get_hot()
    tab = "new"
    topics = Topic.get_topic(1, tab).items
    if request.method == "GET":
        t = request.args.get("tab")
        if t is not None:
            tab = t
        topics = Topic.get_topic(1, tab).items
    return render_template('forum/index.html', topics=topics, hot_topics=hot_topics, tab=tab)


@forum.route('/topic/<int:id>', methods=['POST', 'GET'])
def article(id):
    if current_user.is_authenticated:
        session['msg_num'] = Message.get_user_unread_num(current_user.id)
    page = request.args.get("p", 1, type=int)
    topic = Topic.query.get(id)
    pagination, replies = Reply.topic_reply(id, page)
    form = ReplyForm()
    topic.add_click_rate()
    if request.method == "POST":
        if form.validate_on_submit():
                reply = Reply(form.content.data, current_user.id, current_user.username, id)
                try:
                    reply.save()
                    return redirect(url_for('.article', id=id))
                except:
                    flash("Reply failed", "danger")
        if request.form["action"]=="add_vote":
            if topic.into_topic_liked(current_user.username):
                current_user.collect_topic(topic.id)
                return json.dumps({"status": "ok"})
    if topic is None:
        return "Topic missed"
    return render_template('forum/article.html', topic=topic, replies=replies, form=form, pagination=pagination)


@forum.route('/about')
def about():
    return render_template('about.html')


@forum.route('/faq')
def faq():
    return redirect(url_for(".index"))


@forum.route('/advertise')
def advertise():
    return render_template('advertise.html')


@forum.route('/post', methods=['POST', 'GET'])
@login_required
def post():
    form = PostForm()
    if form.validate_on_submit():
        topic =Topic(form.title.data,
                     form.content.data,
                     current_user.id,
                     form.label.data)
        try:
            topic.save()
            flash('Post success', 'success')
            return redirect(url_for('.index'))
        except:
            flash('Failed', 'danger')
    return render_template('forum/post.html', form=form)


@forum.route('/edit/t/<int:id>', methods=['GET', 'POST'])
def edit(id):
    form = PostForm()
    topic = Topic.query.get(id)
    if form.validate_on_submit():
        topic.title = form.title.data
        topic.content = form.content.data
        topic.label = form.label.data
        topic.music_chain = form.music_chain.data
        try:
            topic.save(action="edit")
            flash('success', 'success')
            return redirect(url_for('.index'))
        except:
            flash('failed', 'danger')
    return render_template("forum/edit.html", form=form, topic=topic)


@forum.route('/new', methods=['GET', 'POST'])
def recent():
    page = request.args.get("p")
    topics = Topic.get_topic(page, "new")
    return render_template("forum/t_list.html", topics=topics, label="recent")


@forum.route('/cn', methods=['GET', 'POST'])
def cn():
    page = request.args.get("p")
    topics = Topic.get_topic(page, "cn")

    return render_template("forum/t_list.html", topics=topics, label="cn")


@forum.route('/en', methods=['GET', 'POST'])
def en():
    page = request.args.get("p")
    topics = Topic.get_topic(page, "en")

    return render_template("forum/t_list.html", topics=topics, label="en")


@forum.route('/jk', methods=['GET', 'POST'])
def jk():
    page = request.args.get("p")
    topics = Topic.get_topic(page, "jk")

    return render_template("forum/t_list.html", topics=topics, label="jk")


@forum.route('/ins', methods=['GET', 'POST'])
def ins():
    page = request.args.get("p")
    topics = Topic.get_topic(page, "ins")

    return render_template("forum/t_list.html", topics=topics, label="ins")


@forum.route('/other', methods=['GET', 'POST'])
def other():
    page = request.args.get("p")
    topics = Topic.get_topic(page, "other")

    return render_template("forum/t_list.html", topics=topics, label="other")


@forum.route('/search', methods=['POST'])
def search():
    if request.method == "POST":
        t = request.form.get('search_text')
        url = 'https://www.google.com/search?q=site:www.0tinn.com ' + t
        return redirect(url)


@forum.route('/how')
def how():

    return redirect(url_for(".index"))
