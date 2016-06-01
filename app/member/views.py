# -*- coding:utf-8 -*-
from flask import Blueprint, render_template, session, request, redirect, flash, url_for, jsonify
from flask_login import login_user, login_required, logout_user, current_user
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
        return "No this member"
    return render_template('user/index.html', user=user, topics=topics, replies=replies, msg=msg, form=form, letters=letter, like_topics=like_topics)


@member.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        flash('Already sign in', 'info')
        return redirect('/')
    form = SignupForm()
    if form.validate_on_submit():
        user = form.save()
        try:
            send_confirm_email(user, user.set_token())
        except:
            print('send email failed!')
        login_user(user)
        flash('Sign up success, do not to your email to check mail', 'success')
        return redirect("/")
    return render_template('user/signup.html', form=form)


@member.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Already sign in', "info")
        return redirect("/")
    form = LoginForm()
    if form.validate_on_submit():
        user, authonticated = Member.authenticate(form.email.data, form.password.data)
        if authonticated:
            login_user(user, form.remeber_me.data)
            return redirect("/")
        else:
            flash("email or password not correct", 'warning')
    return render_template('user/login.html', form=form)


@member.route('/signout', methods=['GET', 'POST'])
@login_required
def signout():
    logout_user()
    return ""


@member.route("/forget", methods=["GET", "POST"])
def forget():
    if request.method == "GET":
        email = request.args.get("email")
        if email is not None:
            user = Member.query.filter_by(email=email).first()
            if user is None:
                return "email error"
            try:
                send_reset_email(user, user.set_token(), email)
                return "sended"
            except:
                return "failed"
    return render_template("user/forget.html")


@member.route('/confirm/<token>', methods=['GET', 'POST'])
@login_required
def confirm(token):
    if current_user.is_confirmed:
        return "Don't be naughty"
    if current_user.confirm(token):
        flash('Activate success', 'success')
        return redirect("/")
    return "failed"


@member.route('/reset_pw/<string:email>/<token>', methods=['GET', 'POST'])
def reset_pw(email, token):
    form = ResetpwForm()
    user = Member.query.filter_by(email=email).first()
    if user.confirm(token):
        if form.validate_on_submit():
            user.set_pw(form.password.data)
            flash('Reset success', 'success')
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
            flash('Save success', 'success')
        except:
            print('Save failed.')
    return render_template('user/setting.html', form=form)


@member.route('/send_confirm/<int:id>', methods=['GET', 'POST'])
@login_required
def send_confirm(id):
    if request.method == "POST":
        user = Member.query.get(id)
        if user.username == current_user.username:
            send_confirm_email(user, user.set_token())
        else:
            return "Don't be naughty"
    return "-_-"


@member.route("/follow", methods=["POST", "GET"])
@login_required
def deal_follow():
    if request.method == "GET":
        u_id = request.args.get("u_id")
        action = request.args.get('action')
        if action == "follow":
            if current_user.following(u_id):
                return 'success'
            else:
                return "failed"
        elif action=="unsubscribe":
            if current_user.remove_following(u_id):
                return "success"
            else:
                return "failed"
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
                    return jsonify({"info": "In success, at present continuous sign {} days".format(current_user.continuous_check_in)})
                else:
                    return jsonify({"info": "Sign in success"})
            else:
                return jsonify({"info": "Sign in failure"})
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
