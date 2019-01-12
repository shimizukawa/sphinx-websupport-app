# -*- coding: utf-8 -*-
"""
    sphinxweb
    ~~~~~~~~~

    A simple Sphinx web support webapp.

    :copyright: Copyright 2007-2010 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import sys
import os
from os import path

from flask import Flask, g, session, url_for, send_from_directory
from flask_mail import Mail, Message

from sphinxcontrib.websupport import WebSupport

app = Flask(__name__, instance_path=os.getcwd(), instance_relative_config=True)
app.config.from_envvar('SPHINXWEB_SETTINGS')

@app.route('/static/_<section>/<path:name>')
def sphinx_statics(section, name):
    directory = path.join(app.config['BUILD_DIR'], 'static', '_' + section)
    return send_from_directory(directory, name)

mail = Mail(app)

from sphinxweb.models import db_session, User

NEW_COMMENT_MAIL = '''\
A new comment has been submitted for moderation:

Document: %(document)s
Author: %(username)s
Text:
%(text)s

Proposal:
%(proposal)s

Moderate: %(url)s
'''

def moderation_callback(comment):
    if not app.config['NOTIFY']:
        return
    doc_url = url_for('docs.doc', docname=comment['document'], _external=True)
    msg = Message('New comment on ' + doc_url,
                  recipients=app.config['NOTIFY'])
    moderate_url = doc_url + '#comment-' + comment['node']
    msg.body = NEW_COMMENT_MAIL % {'document': comment['document'],
                                   'username': comment['username'],
                                   'text':     comment['original_text'],
                                   'proposal': comment['proposal_diff_text'],
                                   'url':      moderate_url,
                                   }
    try:
        mail.send(msg)
    except Exception as err:
        print >>sys.stderr, 'mail not sent:', err  # for now

support = WebSupport(datadir=path.join(app.config['BUILD_DIR'], 'data'),
                     search=app.config['SEARCH'],
                     docroot='',
                     storage=app.config['DATABASE_URI'],
                     moderation_callback=moderation_callback)

@app.context_processor
def inject_globalcontext():
    """Inject "sg", the global context."""
    return dict(sg=support.get_globalcontext())

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.filter_by(openid=session['user_id']).first()

@app.after_request
def after_request(response):
    db_session.remove()
    return response

from . import docs, auth
app.register_blueprint(docs.docs)
app.register_blueprint(auth.auth)
