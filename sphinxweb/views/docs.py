# -*- coding: utf-8 -*-
"""
    sphinxweb.views.docs
    ~~~~~~~~~~~~~~~~~~~~

    Views for the Sphinx Web Support app.

    :copyright: Copyright 2007-2010 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from os import path
from flask import Module, render_template, request, g, abort, jsonify
from sphinx.websupport import WebSupport
from sphinx.websupport.errors import UserNotAuthorizedError, \
     DocumentNotFoundError
from sphinxweb import app

docs = Module(__name__)

support = WebSupport(datadir=path.join(app.config['BUILD_DIR'], 'data'),
                     search=app.config['SEARCH'],
                     docroot='',
                     storage=app.config['DATABASE_URI'])

sg = support.get_globalcontext()

@docs.route('/')
def index():
    return doc('')

@docs.route('/<path:docname>/')
def doc(docname):
    username = g.user.name if g.user else ''
    moderator = g.user.moderator if g.user else False
    try:
        document = support.get_document(docname, username, moderator)
    except DocumentNotFoundError:
        abort(404)
    return render_template('doc.html', document=document, sg=sg)

@docs.route('/search/')
def search():
    document = support.get_search_results(request.args.get('q', ''))
    return render_template('doc.html', document=document, sg=sg)

@docs.route('/_get_comments')
def get_comments():
    username = g.user.name if g.user else None
    moderator = g.user.moderator if g.user else False
    node_id = request.args.get('node', '')
    data = support.get_data(node_id, username, moderator=moderator)
    return jsonify(**data)

@docs.route('/_add_comment', methods=['POST'])
def add_comment():
    parent_id = request.form.get('parent', '')
    node_id = request.form.get('node', '')
    text = request.form.get('text', '')
    proposal = request.form.get('proposal', '')
    username = g.user.name if g.user is not None else 'Anonymous'
    comment = support.add_comment(text, node_id=node_id, parent_id=parent_id,
                                  username=username, proposal=proposal)
    return jsonify(comment=comment)

@docs.route('/_accept_comment', methods=['POST'])
def accept_comment():
    moderator = g.user.moderator if g.user else False
    comment_id = request.form.get('id')
    support.accept_comment(comment_id, moderator=moderator)
    return 'OK'

@docs.route('/_reject_comment', methods=['POST'])
def reject_comment():
    moderator = g.user.moderator if g.user else False
    comment_id = request.form.get('id')
    support.reject_comment(comment_id, moderator=moderator)
    return 'OK'

@docs.route('/_delete_comment', methods=['POST'])
def delete_comment():
    moderator = g.user.moderator if g.user else False
    username = g.user.name if g.user else ''
    comment_id = request.form.get('id')
    try:
        support.delete_comment(comment_id, username=username,
                               moderator=moderator)
    except UserNotAuthorizedError:
        abort(401)
    return 'OK'

@docs.route('/_process_vote', methods=['POST'])
def process_vote():
    if g.user is None:
        abort(401)
    comment_id = request.form.get('comment_id')
    value = request.form.get('value')
    if value is None or comment_id is None:
        abort(400)
    support.process_vote(comment_id, g.user.name, value)
    return "success"
