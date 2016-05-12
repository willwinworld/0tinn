# -*- coding:utf-8 -*-
class config():
    DEBUG = False

    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:boxiao@localhost:3306/ms?charset=utf8'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    SECRET_KEY = 'sdfDdf?/.adfavAJLKJIOJFDskldjf'

    # Mail
    MAIL_SERVER = 'smtp-mail.outlook.com'
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'tallone_s@outlook.com'
    MAIL_PASSWORD = 'boxiao123'
    MAIL_DEFAULT_SENDER = ('0tinn社区', 'tallone_s@outlook.com')
