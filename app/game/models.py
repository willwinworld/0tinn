# -*- coding:utf-8 -*-
from app.extensions import db
from app.util.helper import now_time
from app.extensions import redis_store
from app.member.models import Member
from app.message.models import Message
from app.util.helper import is_discuss

class Game_News(db.Model):
    __tablename__ = "game_news"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    pic = db.Column(db.String(200), nullable=False)
    sentence = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=now_time())

    def __repr__(self):
        return "<{}.{}>".format(self.__class__.__name__, self.id)

    def __init__(self, title, sentence, content, pic):
        self.title = title
        self.sentence = sentence
        self.content = content
        self.pic = pic

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get(cls, page):
        return cls.query.order_by(cls.date_created.desc()).paginate(page, 20, False)

    @classmethod
    def get_hot(cls):
        id = redis_store.get("gnews_hot")
        return cls.query.get(int(id))

    @staticmethod
    def set_hot(id):
        redis_store.set("gnews_hot", id)


class Gnews_Reply(db.Model):
    __tablename__ = "g_reply"
    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=now_time())
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return "<{}.{}>".format(self.__class__.__name__, self.id)

    def __init__(self, id, u_id, name, content):
        self.news_id = id
        self.user_id = u_id
        self.username = name
        self.content = content

    def save(self):
        news = Game_News.query.get(self.news_id)
        l_user = is_discuss(self.content)
        if l_user is not None:
            for u in l_user:
                user = Member.query.filter_by(username=u).first()
                if user:
                    t = "<a href='/member/" + u + "'>" + u + "</a>"
                    self.content = self.content.replace(u, t)
                    msg_ct = self.username + "在" + "\"" + news.title + "\"中@了你"
                    msg = Message(user.id, self.user_id, None, msg_ct)
                    msg.save()
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def get_user(self):
        u = Member.query.get(self.user_id)
        return u

    @classmethod
    def get(cls, nid):
        return cls.query.filter_by(news_id=nid).all()

