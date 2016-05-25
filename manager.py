#   -*- coding:utf-8 -*-
from flask_script import Manager
from app import create_app
from app.extensions import db

app = create_app()
manager = Manager(app)

from app.message import Message, Pri_letter
from app.forum import Topic, Reply
from app.member import Member


@manager.command
def init_db():
    db.create_all()


@manager.command
def drop_db():
    db.drop_all()

if __name__ == '__main__' :
    manager.run()
