# -*- coding:utf-8 -*-
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from .models import Message, Pri_letter

message = Blueprint("messages", __name__)


@message.route('/message/<int:id>', methods=['GET', 'POST'])
@login_required
def handle(id):
    if request.method == "POST":
        msg = Message.query.get(id)
        action = request.form["action"]
        if action=="readed":
            msg.set_readed()
        elif action == "delete":
            msg.delete()
    return "0.0"


@message.route('/letter', methods=['GET', 'POST'])
@login_required
def letter():
    if request.method == "POST":
        ct = request.form['content']
        if ct == "":
            return jsonify(info="Content can not be empty")
        else:
            u_id = request.form["userId"]
            l = Pri_letter(current_user.username, current_user.id, u_id, ct)
            try:
                l.save()
                return jsonify(info="successs")
            except:
                return jsonify(info="failed")
    if request.method == "GET":
        action = request.args.get('action')
        l_id = request.args.get("letter_id")
        if action == "delete":
            l = Pri_letter.query.get(l_id)
            l.delete()
    return "0.0"
