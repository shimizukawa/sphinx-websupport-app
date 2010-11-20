# -*- coding: utf-8 -*-
"""
    sphinxweb
    ~~~~~~~~~

    A simple Sphinx web support webapp.

    :copyright: Copyright 2007-2010 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from flask import Flask, g, session

app = Flask(__name__)
app.config.from_envvar('SPHINXWEB_SETTINGS')
app.root_path = app.config['BUILD_DIR']

from sphinxweb.models import db_session, User

@app.before_request
def before_request():
    g.user = None
    if 'openid' in session:
        g.user = User.query.filter_by(openid=session['openid']).first()

@app.after_request
def after_request(response):
    db_session.remove()
    return response

from sphinxweb.views.docs import docs
from sphinxweb.views.auth import auth
app.register_module(docs)
app.register_module(auth)
