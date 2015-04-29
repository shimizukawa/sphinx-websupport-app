# -*- coding: utf-8 -*-
"""
    sphinxweb make-user-permission
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Script to make a user a moderator.

    :copyright: Copyright 2007-2010 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
import sys
from flask import Flask
from sqlalchemy.orm.exc import NoResultFound

from .models import db_session, User, Permission

app = Flask(__name__)

app.config.from_envvar('SPHINXWEB_SETTINGS')

def make_user_permission(email, permission):
    session = db_session()
    user = session.query(User).filter(User.email == email).one()
    if user is None:
        return False

    if permission in user.permission_names:
        return True

    q = session.query(Permission).filter(Permission.name == permission)
    if q:
        p = q.one()
    else:
        p = Permission(permission)

    user.permissions.append(p)
    session.commit()
    session.close()
    return True


def main():
    email, permission = sys.argv[1:]
    if not email:
        print "usage: python make-user-permission.py user@gmail.com read"

    if not make_user_permission(email, permission):
        print "email address %s not found" % email


if __name__ == '__main__':
    main()
