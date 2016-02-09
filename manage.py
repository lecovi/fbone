#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask.ext.script import Manager

from fbone import create_app
from fbone.extensions import db
from fbone.user import User, UserDetail, ADMIN, ACTIVE
from fbone.utils import MALE


app = create_app()
manager = Manager(app)


@manager.command
def run():
    """Run in local machine."""

    app.run()


@manager.command
def initdb():
    """Init/reset database."""

    db.drop_all()
    db.create_all()

    admin = User(
            name='bitson',
            email='bitson@bitson.com.ar',
            password='bitson',
            role_code=ADMIN,
            status_code=ACTIVE,
            user_detail=UserDetail(
                sex_code=MALE,
                age=10,
                url='http://bitson.com.ar',
                deposit=100.00,
                location='Ciudad Autónoma de Buenos Aires',
                bio='Buby is our admin Guy, he is... hmm... just a admin guy.'))
    db.session.add(admin)
    db.session.commit()


manager.add_option('-c', '--config',
                   dest="config",
                   required=False,
                   help="config file")

if __name__ == "__main__":
    manager.run()
