# -*- coding:utf-8 -*-
import hashlib
import random
from datetime import datetime
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db, redis_store
from app.util.helper import now_time, check_in_time_format


class Member(db.Model, UserMixin):
    __tablename__ = 'member'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    date_joined = db.Column(db.DateTime, default=now_time())
    lastseen = db.Column(db.DateTime, default=now_time())
    gender = db.Column(db.String(10), default='genderless')
    signature = db.Column(db.Text)
    avatar = db.Column(db.String(200))
    is_confirmed = db.Column(db.Boolean, default=False)
    is_check_in = db.Column(db.Boolean, default=False)
    last_check_in = db.Column(db.DateTime)
    longest_check_in = db.Column(db.Integer, default=0)
    continuous_check_in = db.Column(db.Integer, default=0)
    total_check_in = db.Column(db.Integer, default=0)
    wealth = db.Column(db.Integer, default=1000)

    @staticmethod
    def member_num():
        return Member.query.count()

    @property
    def following_num(self):
        return len(self.get_following())

    @property
    def follower_num(self):
        return len(self.get_follower())

    @property
    def collect_topic_num(self):
        return len(self.get_collect_topics())

    @classmethod
    def authenticate(cls, account, pwd):
        user = cls.query.filter(db.or_(cls.email == account, cls.username == account)).first()
        if user:
            authenticated = user.check_pwd(pwd)
        else:
            authenticated = False
        return user, authenticated

    def __init__(self, emai, username, password):
        self.email = emai
        self.username = username
        self.password = generate_password_hash(password)
        self.avatar = self.default_gravater()

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.username)

    def set_pw(self, pw):
        self.password = generate_password_hash(pw)
        self.save()

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def set_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.is_confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def check_pwd(self, pwd):
        return check_password_hash(self.password, pwd)

    def default_gravater(self,  default='monsterid'):
        url = 'https://cdn.v2ex.com/gravatar'
        hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return "{}/{}?d={}".format(url, hash, default)

    def collect_topic(self, topic_id):
        if not redis_store.sismember("user_like_topics:{}".format(self.id), topic_id):
            redis_store.sadd("user_like_topics:{}".format(self.id), topic_id)
            return True
        return False

    def get_collect_topics(self):
        topics = redis_store.smembers("user_like_topics:{}".format(self.id))
        return topics

    def following(self, u_id):
        if not redis_store.sismember("user_following:{}".format(self.id), u_id):
            redis_store.sadd("user_follower:{}".format(u_id), self.id)
            redis_store.sadd("user_following:{}".format(self.id), u_id)
            return True
        return False

    def remove_following(self, u_id):
        if redis_store.sismember("user_follower:{}".format(u_id), self.id):
            redis_store.srem("user_follower:{}".format(u_id), self.id)
            redis_store.srem("user_following:{}".format(self.id), u_id)
            return True
        return False

    def is_followed(self, u_id):
        if redis_store.sismember("user_following:{}".format(self.id), u_id):
            return True
        return False

    def get_following(self):
        users = []
        for f in redis_store.smembers("user_following:{}".format(self.id)):
            users.append(Member.query.get(int(f)))
        return users

    def get_follower(self):
        users = []
        for f in redis_store.smembers("user_follower:{}".format(self.id)):
            users.append(Member.query.get(int(f)))
        return users

    def check_in(self):
        if self.is_check_in:
            return False
        t = int(check_in_time_format(datetime.now()))
        if self.last_check_in is not None:
            l_t = int(check_in_time_format(self.last_check_in))
            x = t - l_t
            if x == 1 or x in range(70, 74):
                self.continuous_check_in += 1
                if self.continuous_check_in > self.longest_check_in:
                    self.longest_check_in = self.continuous_check_in
            else:
                self.continuous_check_in = 0
        self.total_check_in += 1
        self.is_check_in = True
        self.last_check_in = now_time()
        w = random.randint(5, 41)
        self.wealth_action(w)
        b = Bill(self.id, "每日签到", w, self.wealth)
        try:
            b.save()
            self.save()
        except:
            return False
        return True

    def wealth_action(self, num):
        self.wealth = self.wealth + num
        if self.wealth < 0:
            self.wealth = 0
        self.save()

    def get_bill(self, page):
        b = Bill.query.filter_by(user_id=self.id).order_by(Bill.time_created.desc()).paginate(page, 40, False)
        return b


class Bill(db.Model):
    __tablename__ = "consumption"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    time_created = db.Column(db.DateTime, default=now_time())
    types = db.Column(db.String(100), nullable=False)
    nums = db.Column(db.Integer)
    balance = db.Column(db.Integer)

    def __init__(self, id, type, num, balance):
        self.user_id = id
        self.types = type
        self.nums = num
        self.balance = balance

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.id)

    def save(self):
        db.session.add(self)
        db.session.commit()
