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
from sqlalchemy.orm.exc import NoResultFound

from .models import db_session, User

app = Flask(__name__)

app.config.from_envvar('SPHINXWEB_SETTINGS')

def make_moderator(email):
    session = db_session()
    nusers = session.query(User).filter(User.email == email).\
             update({User.moderator: True})
    session.commit()
    session.close()
    return nusers


def main():
    emails = sys.argv[1:]
    if not emails:
        print "usage: python make-moderator.py user@gmail.com ..."

    for email in emails:
        if not make_moderator(email):
            print "email address %s not found" % email


if __name__ == '__main__':
    main()
