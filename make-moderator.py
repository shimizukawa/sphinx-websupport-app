# -*- coding: utf-8 -*-
"""
    sphinxdemo.make-moderator
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Script to make a user a moderator.

    :copyright: Copyright 2007-2010 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
import sys
from flask import Flask
from sphinxdemo.models import db_session, User
from sqlalchemy.orm.exc import NoResultFound

app = Flask(__name__)

app.config.from_envvar('SPHINXDEMO_SETTINGS')

def make_moderator(email):
    session = db_session()
    try:
        session.query(User).filter(User.email == email).\
            update({User.moderator: True})
        session.commit()
    finally:
        session.close()

if __name__ == '__main__':
    try:
        emails = sys.argv[1:]
    except IndexError:
        print "usage: python make-moderator.py user@gmail.com"

    for email in emails:
        try:
            make_moderator(email)
        except NoResultFound:
            print "email address %s not found" % email
