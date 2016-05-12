# -*- coding:utf-8 -*-
from app.extensions import db
from app.util.helper import now_time


class Message(db.Model):
    # 提醒
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    from_user_id = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.DateTime, default=now_time())
    unread = db.Column(db.Boolean, nullable=False, default=True)
    content = db.Column(db.String(200), nullable=False)
    topic_id = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.id)

    def __init__(self, user_id, from_user_id, topic_id, content):
        self.user_id = user_id
        self.from_user_id = from_user_id

        if topic_id is None:
            pass
        else:
            self.topic_id = topic_id
        self.content = content

    @classmethod
    def get_user_message(cls, u_id):
        msg = cls.query.filter_by(user_id=u_id).order_by(cls.date_created.desc()).all()
        return msg

    @classmethod
    def get_user_unread_num(cls, u_id):
        num = cls.query.filter_by(user_id=u_id).filter_by(unread=True).count()
        return num

    def set_readed(self):
        self.unread = False
        self.save()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def save(self):
        db.session.add(self)
        db.session.commit()


class Pri_letter(db.Model):
    # 私信
    __tablename__ = 'pri_letter'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200))
    from_user_id = db.Column(db.Integer, nullable=False)
    to_user_id = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.DateTime, default=now_time())
    content = db.Column(db.Text)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.id)

    def __init__(self, username, from_user_id, to_user_id, content):
        self.username = username
        self.from_user_id = from_user_id
        self.to_user_id = to_user_id
        self.content = content

    @staticmethod
    def get_user_letter(u_id):
        return Pri_letter.query.filter_by(from_user_id=u_id).order_by(Pri_letter.date_created.desc()).all()

    @staticmethod
    def get_letter_num(u_id):
        return Pri_letter.query.filter_by(from_user_id=u_id).order_by(Pri_letter.date_created.desc()).count()

    def save(self):
        m = "收到了来自" + self.username + "的私信"
        msg = Message(self.to_user_id, self.from_user_id, None, m)
        try:
            msg.save()
        except:
            print("私信发送失败,{}".format(self.id))

        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()