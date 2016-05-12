# -*- coding:utf-8 -*-
from app.member.models import Member, Bill
from app.message.models import Message
from app.extensions import db
from app.util.helper import now_time, is_discuss, get_score
from app.extensions import redis_store

import datetime


class Topic(db.Model):
    __tablename__ = 'topic'
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
#   少一次查询是一次
    username = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=now_time())
    vote = db.Column(db.Integer, default=0)
    click_rate = db.Column(db.Integer, default=1)
    music_chain = db.Column(db.String(255), nullable=False)
    last_reply = db.Column(db.String(200))
    last_active = db.Column(db.DateTime, default=now_time())

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.id)

    def __init__(self, title, content, user_id, music_chain, label):
        self.title = title
        self.content = content
        self.user_id = user_id
        self.music_chain = music_chain
        self.label = label

        self.username = self.get_user().username

    @classmethod
    def get_topic(cls, page, label):
        global topics
        if label == "new":
            topics = Topic.query.order_by(Topic.date_created.desc()).paginate(page, 30, False)
        elif label == "cn":
            topics = Topic.query.filter_by(label="国语").order_by(Topic.last_active.desc()).paginate(page, 30, False)
        elif label == "en":
            topics = Topic.query.filter_by(label="欧美").order_by(Topic.last_active.desc()).paginate(page, 30, False)
        elif label == "jk":
            topics = Topic.query.filter_by(label="日韩").order_by(Topic.last_active.desc()).paginate(page, 30, False)
        elif label == "ins":
            topics = Topic.query.filter_by(label="纯音乐").order_by(Topic.last_active.desc()).paginate(page, 30, False)
        else:
            topics = Topic.query.filter_by(label="其它").order_by(Topic.last_active.desc()).paginate(page, 30, False)
        return topics

    @classmethod
    def get_hot(cls):
        d = datetime.datetime.now() + datetime.timedelta(-3)
        d = d.strftime("%Y-%m-%d %H:%M:%S")
        topics = cls.query.filter(cls.date_created >= d).all()
        x = []
        if topics is None:
            return None
        for t in topics:
            score = get_score(t.click_rate, t.vote, t.reply_num)
            redis_store.zadd("Hot_topics", score, t.id)
        for i in redis_store.zrevrange("Hot_topics", 0, 6):
            x.append(cls.query.get(int(i)))
        return x

    @staticmethod
    def get_user_topic_num(username):
        num = Topic.query.filter_by(username=username).count()
        return num

    @staticmethod
    def get_user_topic(username):
        topic = Topic.query.filter_by(username=username).all()
        return topic

    @staticmethod
    def total_topics():
        num = Topic.query.count()
        return num

    @property
    def reply_num(self):
        num = Reply.query.filter_by(topic_id=self.id).count()
        return num

    @property
    def liked_num(self):
        return redis_store.scard("topic_liked:{}".format(self.id))

    def get_user(self):
        user = Member.query.get(self.user_id)
        return user

    def add_click_rate(self):
        self.click_rate += 1
        db.session.add(self)
        db.session.commit()

    def into_topic_liked(self, username):
        if not redis_store.sismember("topic_liked:{}".format(self.id), username):
            redis_store.sadd("topic_liked:{}".format(self.id), username)
            return True
        return False

    def save(self, action="post"):
        u = self.get_user()
        if action=="post":
            u.wealth_action(-20)
            b = Bill(u.id, "创建主题", -20, u.wealth)
        elif action=="edit":
            u.wealth_action(-5)
            b = Bill(u.id, "编辑主题", -5, u.wealth)
        try:
            u.save()
            b.save()
        except:
            return False
        db.session.add(self)
        db.session.commit()


class Reply(db.Model):
    __tablename__ = 'reply'
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=now_time())
    topic_floor = db.Column(db.Integer, default=0)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.id)

    def __init__(self, content, user_id, username, topic_id):
        self.content = content
        self.user_id = user_id
        self.username = username
        self.topic_id = topic_id

    @staticmethod
    def reply_num():
        return Reply.query.count()

    @staticmethod
    def get_user_reply(username):
        return Reply.query.filter_by(username=username).order_by(Reply.date_created.desc()).all()

    @classmethod
    def topic_reply(cls, topic_id, page):
        pagination = cls.query.filter_by(topic_id=topic_id).order_by(cls.topic_floor).paginate(page, 100, False)
        replies = [r for r in pagination.items]
        return pagination, replies

    def get_user(self):
        user = Member.query.get(self.user_id)
        return user

    def get_topic(self):
        return Topic.query.get(self.topic_id)

    def save(self):
        topic = self.get_topic()
        topic.last_reply = self.username
        topic.last_active = now_time()
        db.session.add(topic)
        db.session.commit()
        r = Reply.query.filter_by(topic_id=self.topic_id).order_by(Reply.topic_floor.desc()).first()
        if r is None:
            self.topic_floor = 1
        else:
            self.topic_floor = r.topic_floor + 1

        l_user = is_discuss(self.content)
        if l_user is not None:
            for u in l_user:
                user = Member.query.filter_by(username=u).first()
                if user:
                    t = "<a href='/member/" + u + "'>" + u + "</a>"
                    self.content = self.content.replace(u, t)
                    msg_ct = self.username + "在" + "\"" + topic.title + "\"中@了你"
                    msg = Message(user.id, self.user_id, topic.id, msg_ct)
                    msg.save()
        r_u = self.get_user()
        r_u.wealth_action(-5)
        r_b = Bill(r_u.id, "发表回复", -5, r_u.wealth)
        t_u = self.get_topic().get_user()
        if r_u.username != t_u.username:
            t_u.wealth_action(5)
            t_b = Bill(t_u.id, "主题收益", 5, t_u.wealth)
            t_b.save()
            t_u.save()
        try:
            r_u.save()
            r_b.save()
        except:
            return False
        db.session.add(self)
        db.session.commit()
