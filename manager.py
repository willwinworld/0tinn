#   -*- coding:utf-8 -*-
from flask_script import Manager
from app import create_app
from app.extensions import db, admin
from app.util.helper import AdminViews, LetterView

app = create_app()
manager = Manager(app)

from app.message import Message, Pri_letter
from app.forum import Topic, Reply
from app.member import Member


admin.add_view(AdminViews(Member, db.session))
admin.add_view(AdminViews(Message, db.session, category="Message"))
admin.add_view(LetterView(Pri_letter, db.session, category='Message'))
admin.add_view(AdminViews(Topic, db.session, category="Forum"))
admin.add_view(AdminViews(Reply, db.session, category="Forum"))


@manager.command
def init_db():
    db.create_all()


@manager.command
def drop_db():
    db.drop_all()

if __name__ == '__main__' :
    manager.run()
