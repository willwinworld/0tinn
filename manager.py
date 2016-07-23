#   -*- coding:utf-8 -*-
import arrow
from flask_script import Manager
from flask_migrate import MigrateCommand
from app import create_app
from app.extensions import db

app = create_app()
manager = Manager(app)
manager.add_command('db', MigrateCommand)


from app.member.forms import LoginForm
from app.game.models import Popular_games


# Some Information
@app.context_processor
def utility_processor():

    def info(s):
        if s == "topgames":
            return Popular_games.get_topgame()
        elif s == "upcoming":
            return Popular_games.get_upcoming()
    return dict(get_value=info)


@app.context_processor
def forms():
    login_form = LoginForm()
    return dict(login_form=login_form)


# Custom filters
def custom_date(t):
    l = arrow.get(t, 'YYYY-MM-DD HH:mm:ss')
    return l.format('MMM DD, YYYY')


def humanize_date(t):
    l = arrow.get(t, 'YYYY-MM-DD HH:mm:ss')
    return l.humanize()


env = app.jinja_env
env.filters['custom_date'] = custom_date
env.filters['humanize_date'] = humanize_date


@manager.command
def init_db():
    db.create_all()


@manager.command
def drop_db():
    db.drop_all()

if __name__ == '__main__' :
    manager.run()
