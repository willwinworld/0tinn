# -*- coding:utf-8 -*-
from flask import Blueprint, render_template, session, request, redirect, flash, url_for, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from geetest import GeetestLib
from app.email import send_confirm_email, send_reset_email
from app.message.models import Message, Pri_letter
from app.message.forms import LetterForm
from app.forum.models import Topic, Reply
from .forms import *
from .models import Member
from app.util.helper import mark_online

member = Blueprint('members', __name__)
captcha_id = "a68de1af20340f49c85a2cd6ba4611e3"
private_key = "7e9a00ea63636ff005afa90ab27ff5af"


@member.before_app_request
def mark_current_user_online():
    mark_online(request.remote_addr)


@member.route('/member/<username>', methods=['GET', 'POST'])
def index(username):
    form = LetterForm()
    user = Member.query.filter_by(username=username).first()
    msg = object
    letter = object
    like_topics = []
    if user.collect_topic_num > 0:
        for t_id in user.get_collect_topics():
            like_topics.append(Topic.query.get(int(t_id)))
    if current_user.is_authenticated:
        msg = Message.get_user_message(user.id)
        letter = Pri_letter.get_user_letter(current_user.id)
    topics = Topic.get_user_topic(username)
    replies = Reply.get_user_reply(username)
    if user is None:
        return "没有此人"
    return render_template('user/index.html', user=user, topics=topics, replies=replies, msg=msg, form=form, letters=letter, like_topics=like_topics)


@member.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        flash('已经登录了', 'info')
        return redirect('/')
    form = SignupForm()
    gt = GeetestLib(captcha_id, private_key)
    if form.validate_on_submit():
        challenge = request.form[gt.FN_CHALLENGE]
        validate = request.form[gt.FN_VALIDATE]
        seccode = request.form[gt.FN_SECCODE]
        status = session[gt.GT_STATUS_SESSION_KEY]
        user_id = session["user_id"]
        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        if result:
            user = form.save()
            try:
                send_confirm_email(user, user.set_token())
            except:
                print('send email failed!')
            login_user(user)
            flash('注册成功，待会别忘了去邮箱验证', 'success')
            return redirect("/")
    return render_template('user/signup.html', form=form)


@member.route('/login', methods=['GET', 'POST'])
def login():
    gt = GeetestLib(captcha_id, private_key)
    if current_user.is_authenticated:
        flash('已经登录了', "info")
        return redirect("/")
    form = LoginForm()
    if form.validate_on_submit():
        challenge = request.form[gt.FN_CHALLENGE]
        validate = request.form[gt.FN_VALIDATE]
        seccode = request.form[gt.FN_SECCODE]
        status = session[gt.GT_STATUS_SESSION_KEY]
        user_id = session["user_id"]
        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        if result:
            user, authonticated = Member.authenticate(form.email.data, form.password.data)
            if authonticated:
                login_user(user, form.remeber_me.data)
                return redirect("/")
            else:
                flash("邮箱或密码不正确", 'warning')
    return render_template('user/login.html',form=form)


@member.route('/signout', methods=['GET', 'POST'])
@login_required
def signout():
    logout_user()
    return redirect("/")


@member.route("/forget", methods=["GET", "POST"])
def forget():
    if request.method == "GET":
        email = request.args.get("email")
        if email is not None:
            user = Member.query.filter_by(email=email).first()
            if user is None:
                return "用户不存在"
            try:
                send_reset_email(user, user.set_token(), email)
                return "邮件已发出"
            except:
                return "发送失败"
    return render_template("user/forget.html")


@member.route('/register', methods=["GET"])
def get_captcha():
    user_id = 'test'
    gt = GeetestLib(captcha_id, private_key)
    status = gt.pre_process(user_id)
    session[gt.GT_STATUS_SESSION_KEY] = status
    session["user_id"] = user_id
    response_str = gt.get_response_str()
    return response_str


@member.route('/confirm/<token>', methods=['GET', 'POST'])
@login_required
def confirm(token):
    if current_user.is_confirmed:
        return "不要调皮"
    if current_user.confirm(token):
        flash('激活成功', 'success')
        return redirect("/")
    return "已经失效"


@member.route('/reset_pw/<string:email>/<token>', methods=['GET', 'POST'])
def reset_pw(email, token):
    form = ResetpwForm()
    user = Member.query.filter_by(email=email).first()
    if user.confirm(token):
        gt = GeetestLib(captcha_id, private_key)
        if form.validate_on_submit():
            challenge = request.form[gt.FN_CHALLENGE]
            validate = request.form[gt.FN_VALIDATE]
            seccode = request.form[gt.FN_SECCODE]
            status = session[gt.GT_STATUS_SESSION_KEY]
            user_id = session["user_id"]
            if status:
                result = gt.success_validate(challenge, validate, seccode, user_id)
            else:
                result = gt.failback_validate(challenge, validate, seccode)
            if result:
                user.set_pw(form.password.data)
                flash('重设成功', 'success')
                return redirect(url_for(".login"))
    return render_template("user/resetpw.html", form=form, r_token=token, r_email=email)


@member.route('/setting', methods=['GET', 'POST'])
@login_required
def setting():
    form = SettingForm()
    if form.validate_on_submit():
        current_user.gender = form.gender.data
        current_user.signature = form.signature.data
        avatar_url = form.avatar.data
        if avatar_url:
            key, info = current_user.set_avatar(avatar_url)
            if not key:
                flash(info, 'warning')
                return redirect(url_for(".setting"))
        try:
            current_user.save()
            flash('保存成功', 'success')
        except:
            print('保存失败.')
    return render_template('user/setting.html', form=form)


@member.route('/send_confirm/<int:id>', methods=['GET', 'POST'])
@login_required
def send_confirm(id):
    if request.method == "POST":
        user = Member.query.get(id)
        if user.username == current_user.username:
            send_confirm_email(user, user.set_token())
        else:
            return "不要调皮"
    return "-_-"


@member.route("/follow", methods=["POST", "GET"])
@login_required
def deal_follow():
    if request.method == "GET":
        u_id = request.args.get("u_id")
        action = request.args.get('action')
        if action == "follow":
            if current_user.following(u_id):
                return '关注成功'
            else:
                return "关注失败"
        elif action=="unsubscribe":
            if current_user.remove_following(u_id):
                return "取消成功"
            else:
                return "取消失败"
        elif action=="is_followed":
            if current_user.is_followed(u_id):
                return "yes"
            else:
                return "no"
    return False


@member.route('/check-in', methods=['GET', 'POST'])
@login_required
def check_in():
    if request.method == 'GET':
        if not current_user.is_check_in:
            if current_user.check_in():
                d = current_user.continuous_check_in
                if d != 0:
                    return jsonify({"info": "签到成功,目前连续签到 {} 天".format(current_user.continuous_check_in)})
                else:
                    return jsonify({"info": "签到成功"})
            else:
                return jsonify({"info": "签到失败"})
    return False


@member.route('/balance', methods=['GET', 'POST'])
@login_required
def balance():
    if request.method == "GET":
        page = request.args.get('p')
        if page is not None:
            pagination = current_user.get_bill(page)
        else:
            page = 1
            pagination = current_user.get_bill(page)
    return render_template("user/balance.html", pagination=pagination)
