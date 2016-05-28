# -*- coding:utf-8 -*-
from flask import Blueprint, render_template, request
from app.game.forms import Game_news
from app.game.models import Game_News
from app.forum.models import Topic
from app.member.models import Member
from app.util.decorate import admin_must

adm = Blueprint("adm", __name__)


@adm.route('/adm', methods=['GET', 'POST'])
@admin_must
def index():

    return render_template("admin/index.html")


@adm.route('/adm/forms', methods=['GET', 'POST'])
@admin_must
def forms():
     form = Game_news()

     return render_template("admin/forms.html", form=form)


@adm.route('/adm/manage')
@admin_must
def manage():
    if request.method == "GET":
        page = int(request.args.get("p"))
        tab = request.args.get("tab")
        if tab == "":
            tab = "gnews"
        if page == "":
            page = 1
        if tab == "gnews":
            cells = Game_News.get(page)
        elif tab == "user":
            cells = Member.query.paginate(page, 20, False)
        else:
            cells = Topic.query.paginate(page, 20, True)
    return render_template("admin/manage.html", cells=cells, tab=tab)