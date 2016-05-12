# -*- coding:utf-8 -*-
import os

class config():
    DEBUG = False

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
    MAIL_DEFAULT_SENDER = ('0tinn社区', MAIL_USERNAME)
