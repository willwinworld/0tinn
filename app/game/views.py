# -*- coding:utf-8 -*-
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import current_user, login_required
from app.util.decorate import admin_must
from app.member.forms import LoginForm
from .models import Game_News, Gnews_Reply
from .forms import GnewsReplyForm, Game_news

gnews = Blueprint("gnews", __name__)


@gnews.route('/g', methods=['GET', 'POST'])
def index():
    if request.method == "GET":
        page = request.args.get("p")
        if page is None:
            page = 1
        elif int(page) < 1:
            page = 1
        elif int(page) > 30:
            return 404
        news = Game_News.get(int(page))
    return render_template("game/index.html", news=news)


@gnews.route('/g/<string:title>', methods=['GET', 'POST'])
def detail(title):
    news = Game_News.query.filter_by(title=title).first_or_404()
    news.add_views()
    replies = Gnews_Reply.get(news.id)
    form = GnewsReplyForm()
    return render_template("game/detail.html", news=news, replies=replies, form=form)


@gnews.route("/g/post", methods=["GET", "POST"])
def post():
    if request.method == "GET":
        title = request.args["title"]
        sentence = request.args["sentence"]
        content = request.args['content']
        pic = request.args['pic']
        if title == "" and sentence == "" and content == "" and pic == "":
            return jsonify(info="Failed")
        else:
            gn = Game_News(title, sentence, content, pic)
            try:
                gn.save()
                return jsonify(info="Successed")
            except:
                return jsonify(info="Failed")


@gnews.route('/g/handle_ajax', methods=['GET'])
@login_required
def handle_ajax():
    if request.method == "GET":
        tab = request.args.get("tab")
        action = request.args.get("action")
        id = request.args.get("id")
        if tab == "gnews":
            if action == "set_hot":
                if current_user.username == "Tallone":
                    Game_News.set_hot(id)
            elif action == "post_reply":
                reply_content = request.args.get("content")
                # 对评论内容做判断
                if reply_content == "":
                    return jsonify(info="content is none")
                else:
                    uname = current_user.username
                    uid = current_user.id
                    rep = Gnews_Reply(id=id, u_id=uid,name=uname,content=reply_content)
                    try:
                        rep.save()
                        return jsonify(info="success")
                    except:
                        return jsonify(info="failed")
            elif action == "delete":
                if current_user.username == "Tallone":
                    gn = Game_News.query.get(id)
                    gn.delete()
                    return jsonify(info="Deleted")
        return jsonify(info="OK")


@gnews.route('/g/edit/<int:id>', methods=['GET', 'POST'])
@admin_must
def edit(id):
    o_gn = Game_News.query.get(id)
    form = Game_news()
    if form.validate_on_submit():
        o_gn.title = form.title.data
        o_gn.sentence = form.sentence.data
        o_gn.content = form.content.data
        o_gn.pic = form.pic.data
        o_gn.save()
        return redirect(url_for("adm.manage"))
    return render_template("game/edit.html", news=o_gn, form=form)
