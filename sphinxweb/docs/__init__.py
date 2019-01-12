# -*- coding: utf-8 -*-
"""
    sphinxweb.views.docs
    ~~~~~~~~~~~~~~~~~~~~

    Views for the Sphinx Web Support app.

    :copyright: Copyright 2007-2010 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from flask import (
        Blueprint, render_template, request, g, abort, jsonify, current_app)
from sphinxcontrib.websupport.errors import UserNotAuthorizedError, \
     DocumentNotFoundError

from sphinxweb import support

docs = Blueprint('docs', __name__, template_folder='templates')


def is_moderator(user):
    moderator = g.user.moderator if g.user else False
    return moderator


@docs.route('/')
def index():
    return doc('')

@docs.route('/<path:docname>/')
def doc(docname):
    username = g.user.name if g.user else ''
    moderator = is_moderator(g.user)
    try:
        document = support.get_document(docname, username, moderator)
    except DocumentNotFoundError:
        abort(404)
    return render_template('doc.html', document=document)

@docs.route('/search/')
def search():
    document = support.get_search_results(request.args.get('q', ''))
    return render_template('doc.html', document=document)

@docs.route('/_get_comments')
def get_comments():
    username = g.user.name if g.user else None
    if current_app.config.get('MODERATE_ENABLE', True):
        moderator = is_moderator(g.user)
    else:
        moderator = True
    node_id = request.args.get('node', '')
    data = support.get_data(node_id, username, moderator=moderator)
    return jsonify(**data)

@docs.route('/_add_comment', methods=['POST'])
def add_comment():
    parent_id = request.form.get('parent', '')
    node_id = request.form.get('node', '')
    text = request.form.get('text', '')
    proposal = request.form.get('proposal', '')
    username = g.user.name if g.user is not None else None
    if current_app.config.get('MODERATE_ENABLE', True):
        moderator = is_moderator(g.user)
    else:
        moderator = True
    try:
        comment = support.add_comment(text, node_id, parent_id,
                                      displayed=moderator,
                                      username=username, proposal=proposal,
                                      moderator=moderator)
    except UserNotAuthorizedError:
        abort(401)
    return jsonify(comment=comment)

@docs.route('/_accept_comment', methods=['POST'])
def accept_comment():
    moderator = is_moderator(g.user)
    comment_id = request.form.get('id')
    support.accept_comment(comment_id, moderator=moderator)
    return 'OK'

@docs.route('/_delete_comment', methods=['POST'])
def delete_comment():
    moderator = is_moderator(g.user)
    username = g.user.name if g.user else ''
    comment_id = request.form.get('id')
    try:
        if support.delete_comment(comment_id, username=username,
                                  moderator=moderator):
            return 'delete'
        else:
            return 'mark'
    except UserNotAuthorizedError:
        abort(401)

@docs.route('/_process_vote', methods=['POST'])
def process_vote():
    if g.user is None:
        abort(401)
    comment_id = request.form.get('comment_id')
    value = request.form.get('value')
    if value is None or comment_id is None:
        abort(400)
    support.process_vote(comment_id, g.user.name, value)
    return 'success'
