# -*- coding:utf-8 -*-
from flask import render_template
from flask_mail import Message
from app.extensions import mail, celery


def send_email(subject, recipients, text_body, html_body, sender=None):
    msg = Message(subject, recipients=recipients, sender=sender)
    msg.body = text_body
    msg.html = html_body
    send.delay(msg)


@celery.task
def send(msg):
    mail.send(msg)


def send_confirm_email(user, token):
    send_email(subject='Confirm',
                        recipients=[user.email],
                        text_body=render_template(
                            'email/confirm.txt',
                            user=user,
                            token=token
                        ),
                        html_body=render_template(
                            'email/confirm.html',
                            user=user,
                            token=token,
                        )
    )


def send_reset_email(user, token, email):
    send_email(subject='Reset',
                        recipients=[user.email],
                        text_body=render_template(
                            'email/reset.txt',
                            user=user,
                            token=token,
                            email=email
                        ),
                        html_body=render_template(
                            'email/reset.html',
                            user=user,
                            token=token,
                            email=email
                        )
    )
