# -*- coding:utf-8 -*-
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import current_user, login_required
from .models import Game_News, Gnews_Reply
from .forms import GnewsReplyForm

gnews = Blueprint("gnews", __name__)


@gnews.route('/g', methods=['GET', 'POST'])
def index():
    if request.method == "GET":
        page = request.args.get("p")
        hot = Game_News.get_hot()
        if page is None:
            page = 1
        news = Game_News.get(page)

    return render_template("game/index.html", news=news, hot=hot)


@gnews.route('/g/<int:id>', methods=['GET', 'POST'])
def detail(id):
    news = Game_News.query.filter_by(id=id).first_or_404()
    replies = Gnews_Reply.get(id)
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
            return jsonify(info="失败")
        else:
            gn = Game_News(title, sentence, content, pic)
            try:
                gn.save()
                return jsonify(info="发布成功")
            except:
                return jsonify(info="尝试存入数据库错误")


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
                    return jsonify(info="内容不能为空")
                else:
                    uname = current_user.username
                    uid = current_user.id
                    rep = Gnews_Reply(id=id, u_id=uid,name=uname,content=reply_content)
                    try:
                        rep.save()
                        return jsonify(info="评论成功")
                    except:
                        return jsonify(info="评论失败")
        return jsonify(info="OK")
