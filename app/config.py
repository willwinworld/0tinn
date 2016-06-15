# -*- coding:utf-8 -*-
from __future__ import absolute_import

import os
from celery.schedules import crontab


class config():
    DEBUG = False
    # BOOTSTRAP_SERVE_LOCAL = True
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:boxiao@localhost:3306/0tinn?charset=utf8'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    SECRET_KEY = 'sdfDdf?/.adfavAJLKJIOJFDskldjf'

    # Mail
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT   = 465
    MAIL_USE_TLS = True
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ['EMAIL_USERNAME']
    MAIL_PASSWORD = os.environ['EMAIL_PASSWORD']
    MAIL_DEFAULT_SENDER = ('0tinn', MAIL_USERNAME)

    # RECAPTCHA
    RECAPTCHA_PUBLIC_KEY = '6LcAViETAAAAANLFKQmDl1DtQL_jwa1rMJuoDJVw'
    RECAPTCHA_PRIVATE_KEY = "6LcAViETAAAAAAxdSV7x0qe7ylvPNgp_lgDS1QEX"

    #Celery
    BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    CELERY_IMPORTS = ('app.crawler.dualshockers', 'app.crawler.gnews_crawler', 'app.crawler.wccftech_spider')
    CELERYBEAT_SCHEDULE = {
        'dualshockers-every-3-hour': {
            'task': 'app.crawler.dualshockers.deal_cells',
            'schedule': crontab(minute=0, hour='*/3'),
            'args': ()
        },
        'pcgamer-every-3-hour': {
            'task': 'app.crawler.gnews_crawler.deal_cells',
            'schedule': crontab(minute=0, hour='*/3'),
            'args': ()
        },
        'wccftech-every-3-hour': {
            'task': 'app.crawler.wccftech_spider.deal_cells',
            'schedule': crontab(minute=0, hour='*/3'),
            'args': ()
        },
    }
