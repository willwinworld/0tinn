# -*- coding:utf-8 -*-
from app.extensions import db
from app.util.helper import now_time
from app.util.cache import cached
from app.extensions import redis_store


class Game_News(db.Model):
    __tablename__ = "game_news"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, unique=True)
    pic = db.Column(db.String(200), nullable=False)
    sentence = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.String(20), default=now_time())
    views = db.Column(db.Integer, default=1)

    def __repr__(self):
        return "<{}.{}>".format(self.__class__.__name__, self.id)

    def __init__(self, title, sentence, content, pic):
        self.title = title
        self.sentence = sentence
        self.content = content
        self.pic = pic

    def add_views(self):
        self.views += 1
        self.save()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get(cls, page):
        return cls.query.order_by(cls.id.desc()).paginate(page, 30, False)

    @classmethod
    @cached(timeout=7200, key_name='8-index-news')
    def get_index(cls):
        news = cls.query.order_by(cls.views.desc()).limit(8)
        return news[1:]

    @classmethod
    def get_hot(cls):
        ids = redis_store.lrange("gnews_hot", 0, -1)
        hots = []
        for id in ids:
            new = cls.query.get(int(id))
            hots.append(new)
        return hots

    @staticmethod
    def set_hot(id):
        redis_store.lpush("gnews_hot", id)
        redis_store.ltrim("gnews_hot", 0, 2)


class Popular_games(db.Model):
    __tablename__ = "popular_game"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    date_or_score = db.Column(db.String(30))
    label = db.Column(db.String(20))
    rank = db.Column(db.Integer)

    @classmethod
    @cached(timeout=7200, key_name='top-game')
    def get_topgame(cls):
        games = cls.query.filter_by(label="topgame").all()
        return games

    @classmethod
    @cached(timeout=7200, key_name='upcoming-game')
    def get_upcoming(cls):
        games = cls.query.filter_by(label="upcoming").order_by(cls.rank).all()
        return games

    def __repr__(self):
        return "<{}.{}>".format(self.__class__.__name__, self.name)

    def __init__(self, name, ds, label, rank):
        self.name = name
        self.date_or_score = ds
        self.label = label
        self.rank = rank

    def save(self):
        db.session.add(self)
        db.session.commit()
