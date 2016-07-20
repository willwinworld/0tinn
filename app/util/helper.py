# -*- coding:utf-8 -*-
import re
import time
import arrow
from math import log2
from app.extensions import redis_store


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


def now_time():
    # 格式化时间
    return arrow.utcnow().format('YYYY-MM-DD HH:mm:ss')


def check_in_time_format(t):
    # 签到的时间格式
    return t.strftime("%y%m%d")


def is_discuss(s):
    prog = re.compile(r"@.*?\s")
    result = prog.findall(s)
    if result:
        for r in range(len(result)):
            result[r] = result[r].strip("@ ")
    else:
        return None
    return result

