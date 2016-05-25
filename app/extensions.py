# -*- coding:utf-8 -*-
import redis
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_login import LoginManager
from flask_pagedown import PageDown
from flask_mail import Mail


bootstrap = Bootstrap()

db = SQLAlchemy()

pagedown = PageDown()

login_manager = LoginManager()

moment = Moment()

mail = Mail()

redis_store = redis.StrictRedis("localhost", 6379, 0)

