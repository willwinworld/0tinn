# -*- coding:utf-8 -*-
from flask import Flask
from .extensions import *
from .forum.views import forum
from .member.views import member
from .message.views import message
from .admin.views import adm
from .game.views import gnews
from .member.models import Member
from flaskext.markdown import Markdown


def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.config')
    Markdown(app)
    register_extensions(app)
    register_bprint(app)

    return app


def register_extensions(app):
    bootstrap.init_app(app)
    pagedown.init_app(app)
    db.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    admin.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        user_instance = Member.query.filter_by(id=user_id).first()
        if user_instance:
            return user_instance
        else:
            return None
    login_manager.init_app(app)


def register_bprint(app):
    app.register_blueprint(forum)
    app.register_blueprint(member)
    app.register_blueprint(message)
    app.register_blueprint(adm)
    app.register_blueprint(gnews)