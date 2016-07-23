#   -*- coding:utf-8 -*-
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


@manager.command
def init_db():
    db.create_all()


@manager.command
def drop_db():
    db.drop_all()

if __name__ == '__main__' :
    app.run('0.0.0.0')
