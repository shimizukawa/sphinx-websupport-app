# -*- coding: utf-8 -*-
"""
    sphinxweb make-moderator
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Script to make a user a moderator.

    :copyright: Copyright 2007-2010 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
import sys
from flask import Flask
from sphinxweb.models import db_session, User
from sqlalchemy.orm.exc import NoResultFound

app = Flask(__name__)

app.config.from_envvar('SPHINXWEB_SETTINGS')

def make_moderator(email):
    session = db_session()
    try:
        session.query(User).filter(User.email == email).\
            update({User.moderator: True})
        session.commit()
    finally:
        session.close()

if __name__ == '__main__':
    emails = sys.argv[1:]
    if not emails:
        print "usage: python make-moderator.py user@gmail.com ..."

    for email in emails:
        try:
            make_moderator(email)
        except NoResultFound:
            print "email address %s not found" % email
