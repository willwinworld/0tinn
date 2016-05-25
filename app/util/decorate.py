# -*- coding:utf-8 -*-
from flask_login import current_user
from functools import wraps


def admin_must(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            if current_user.username != "Tallone":
                return "Sorry,you can not view this page"
            else:
                return func(*args, **kwargs)
        else:
            return "Naughty Boy"
    return wrapper