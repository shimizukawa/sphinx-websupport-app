# -*- coding: utf-8 -*-
"""
    sphinxweb.views.auth
    ~~~~~~~~~~~~~~~~~~~~

    Views for the sphinxweb auth system.

    :copyright: Copyright 2007-2010 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from flask import Module, g, request, render_template, session, flash, \
    redirect, url_for, abort

from flaskext.openid import OpenID

from sqlalchemy.exc import IntegrityError

from sphinxweb import support
from sphinxweb.models import User, db_session

auth = Module(__name__)

# setup flask-openid
oid = OpenID()

oid_providers = [
    ('Google', 'google.png', 'https://www.google.com/accounts/o8/id'),
    ('Yahoo', 'yahoo.png', 'http://yahoo.com/'),
    ('myOpenID', 'myopenid.png', 'https://www.myopenid.com/'),
    ('Launchpad', 'launchpad.png', 'https://login.launchpad.net/'),
]


@auth.route('/_login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    """Does the login via OpenID. Has to call into `oid.try_login`
    to start the OpenID machinery.
    """
    # if we are already logged in, go back to were we came from
    if g.user is not None:
        return redirect(oid.get_next_url())
    if request.method == 'POST':
        openid = request.form.get('openid')
        if openid:
            return oid.try_login(openid, ask_for=['email', 'fullname',
                                                  'nickname'])
    return render_template('login.html', next=oid.get_next_url(),
                           error=oid.fetch_error(), oid_providers=oid_providers)


@oid.after_login
def create_or_login(resp):
    """This is called when login with OpenID succeeded and it's not
    necessary to figure out if this is the users's first login or not.
    This function has to redirect otherwise the user will be presented
    with a terrible URL which we certainly don't want.
    """
    session['openid'] = resp.identity_url
    user = User.query.filter_by(openid=resp.identity_url).first()
    if user is not None:
        flash(u'Successfully logged in.')
        g.user = user
        return redirect(oid.get_next_url())
    return redirect(url_for('create_profile', next=oid.get_next_url(),
                            name=resp.fullname or resp.nickname,
                            email=resp.email))


@auth.route('/_create_profile', methods=['GET', 'POST'])
def create_profile():
    """If this is the user's first login, the create_or_login function
    will redirect here so that the user can set up his profile.
    """
    if g.user is not None or 'openid' not in session:
        return redirect(url_for('docs.index'))
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        if not name:
            flash(u'Error: you have to provide a name.')
        elif '@' not in email:
            flash(u'Error: you have to enter a valid email address.')
        else:
            db_session.query(User).filter(User.name == name)
            try:
                db_session.add(User(name, email, session['openid']))
                db_session.commit()
            except IntegrityError:
                flash(u'Error: user name or email address already taken.')
            else:
                flash(u'Profile successfully created.')
                return redirect(oid.get_next_url())
    return render_template('create_profile.html', next_url=oid.get_next_url())


@auth.route('/_profile', methods=['GET', 'POST'])
def edit_profile():
    """Update profile info."""
    if g.user is None:
        abort(401)
    form = dict(name=g.user.name, email=g.user.email)
    if request.method == 'POST':
        if 'delete' in request.form:
            db_session.delete(g.user)
            db_session.commit()
            session['openid'] = None
            flash(u'Profile successfully deleted.')
            return redirect(url_for('docs.index'))
        form['name'] = request.form['name']
        form['email'] = request.form['email']
        if not form['name']:
            flash(u'Error: you have to provide a name.')
        elif '@' not in form['email']:
            flash(u'Error: you have to enter a valid email address.')
        else:
            support.update_username(g.user.name, form['name'])
            try:
                g.user.name = form['name']
                g.user.email = form['email']
                db_session.commit()
            except IntegrityError:
                flash(u'Error: user name or email address already taken.')
            else:
                flash(u'Profile successfully updated.')
                return redirect(url_for('edit_profile'))
    return render_template('edit_profile.html', form=form,
                           openid=session['openid'])

@auth.route('/_logout')
def logout():
    session.pop('openid', None)
    flash(u'You were logged out.')
    return redirect(oid.get_next_url())
