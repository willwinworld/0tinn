# -*- coding:utf-8 -*-
import redis
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_pagedown import PageDown
from flask_mail import Mail
from flask_migrate import Migrate
from celery import Celery

bootstrap = Bootstrap()

db = SQLAlchemy()

pagedown = PageDown()

login_manager = LoginManager()


mail = Mail()

redis_store = redis.StrictRedis("localhost", 6379, 0)

celery = Celery('0Tinn')


migrate = Migrate()