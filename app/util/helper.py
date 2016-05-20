# -*- coding:utf-8 -*-
import json
import requests
import re
import time
from math import log2
from datetime import datetime, timedelta
from app.extensions import redis_store
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

def mark_online(user_id):
    """
    :param user_id: Member id
    参考: http://flask.pocoo.org/snippets/71/
    """
    now = int(time.time())
    expires = now + (5 * 60) + 10
    all_users_key = 'online-users/%d' % (now // 60)
    user_key = 'user-activity/%s' % user_id
    p = redis_store.pipeline()
    p.sadd(all_users_key, user_id)
    p.set(user_key, now)
    p.expireat(all_users_key, expires)
    p.expireat(user_key, expires)
    p.execute()


def get_score(c_rate, vote, reply_num):
    score = log2(c_rate/10) + (2*vote) + (reply_num/10)
    return score


def get_online_user_nums():
    current = int(time.time()) // 60
    minutes = range(5)
    return len(redis_store.sunion(['online-users/%d' % (current - x)
                         for x in minutes]))


def highest_online_number():
    if redis_store.get("Highest_online_number") is not None:
        if get_online_user_nums() > int(redis_store.get("Highest_online_number")):
            redis_store.set("Highest_online_number", get_online_user_nums())
    else:
        redis_store.set("Highest_online_number", get_online_user_nums())
    return int(redis_store.get("Highest_online_number"))


class Tietuku():
    def __init__(self, token):
        self.token = token

    def upload(self, path):
        url = 'http://up.imgapi.com/'
        data = {'Token': self.token}

        try:
            with open(path, 'rb') as f:
                r = requests.post(url, data, files={'file': f})
        except OSError:
            data['fileurl'] = path
            r = requests.post(url, data)

        obj = json.loads(r.text)
        return obj


def now_time():
    # 格式化时间
    td = timedelta(hours=8)
    t = datetime.utcnow() + td
    return t


def check_in_time_format(t):
    # 签到的时间格式
    return t.strftime("%y%m%d")


def up_avatar(url):
    t = Tietuku(
        "423eca86c8fc66f7bf71c07e3cd2f1b5907baec1:QU00WXoxaWdmSWEyTVZ0UGtzallPMmh0dGlvPQ==:eyJkZWFkbGluZSI6MTQ2MjAyNTc0NiwiYWN0aW9uIjoiZ2V0IiwidWlkIjoiNTYzNjcwIiwiYWlkIjoiMTIxNzc3MiIsImZyb20iOiJ3ZWIifQ==")
    res = t.upload(url)
    return res


def is_discuss(s):
    prog = re.compile(r"@.*?\s")
    result = prog.findall(s)
    if result:
        for r in range(len(result)):
            result[r] = result[r].strip("@ ")
    else:
        return None
    return result


def admin_must(u):
    if u.username == "Tallone":
        return True
    else:
        return False


class AdminViews(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return admin_must(current_user)
        else:
            return False


class LetterView(AdminViews):
    column_exclude_list = ["content",]
