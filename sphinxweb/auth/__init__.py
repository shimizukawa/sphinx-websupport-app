# -*- coding: utf-8 -*-
"""
    sphinxweb.views.auth
    ~~~~~~~~~~~~~~~~~~~~

    Views for the sphinxweb auth system.

    :copyright: Copyright 2007-2010 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from flask import Blueprint, g, request, render_template, session, flash, \
    redirect, url_for, abort, current_app
from flask.ext.openid import OpenID
from flask_oauthlib.client import OAuth
from sqlalchemy.exc import IntegrityError

from sphinxweb import support
from sphinxweb.models import User, db_session

auth = Blueprint(
    'auth', __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/auth/static')

# setup flask-openid
oid = OpenID()

oid_providers = [
    ('Launchpad', 'launchpad.png', 'https://login.launchpad.net/'),
]

oauth = OAuth()
google = oauth.remote_app(
    'google',
    request_token_params={'scope': 'email'},
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    app_key='GOOGLE',
)

github = oauth.remote_app(
    'github',
    request_token_params={'scope': 'user:email'},
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    app_key='GITHUB',
)

oauth2_providers = {
    'google': {'api': google, 'resp': 'userinfo', 'icon': 'google.png'},
    'github': {'api': github, 'resp': 'user', 'icon': 'github.png'},
}


@auth.record_once
def on_register(state):
    oauth.init_app(state.app)


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
                           error=oid.fetch_error(),
                           oid_providers=oid_providers,
                           oauth2_provider_icons=[(k, v['icon']) for k, v in oauth2_providers.items()],
                           )


@oid.after_login
def create_or_login(resp):
    """This is called when login with OpenID succeeded and it's not
    necessary to figure out if this is the users's first login or not.
    This function has to redirect otherwise the user will be presented
    with a terrible URL which we certainly don't want.
    """
    session['token_key'] = token_key = 'openid'
    session[token_key] = resp.identity_url
    user = User.query.filter_by(openid=resp.identity_url).first()
    if user is not None:
        flash(u'Successfully logged in.')
        g.user = user
        return redirect(oid.get_next_url())
    return redirect(url_for('.create_profile', next=oid.get_next_url(),
                            name=resp.fullname or resp.nickname,
                            email=resp.email))


@auth.route('/_login_google')
def login_oauth2():
    key = request.args.get('key')
    if key not in oauth2_providers:
        return redirect(url_for('.login'))

    provider = oauth2_providers[key]['api']
    session['token_key'] = key
    return provider.authorize(callback=url_for('.oauth2callback', _external=True))


@auth.route('/_oauth2callback')
def oauth2callback():
    key = session['token_key']
    provider = oauth2_providers[key]['api']
    resp_field = oauth2_providers[key]['resp']

    resp = provider.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session[key] = resp['access_token']
    me = provider.get(resp_field)
    try:
        session['user_id'] = '{key}/{id}'.format(key=key, id=me.data['id'])
        user = User.query.filter_by(openid=session['user_id']).first()
        if user is None:
            return redirect(url_for('.create_profile', next=url_for('docs.index'),
                                    name=me.data['name'], email=me.data['email']))
    except KeyError as e:
        import logging
        logging.exception('KeyError: %r', me.data)
        raise

    flash(u'Successfully logged in.')
    g.user = user
    return redirect(url_for('docs.index'))


@google.tokengetter
def get_google_oauth_token():
    return (session.get('google'), current_app.secret_key)


@github.tokengetter
def get_github_oauth_token():
    return (session.get('github'), current_app.secret_key)


@auth.route('/_create_profile', methods=['GET', 'POST'])
def create_profile():
    """If this is the user's first login, the create_or_login function
    will redirect here so that the user can set up his profile.
    """
    if g.user is not None or 'token_key' not in session or session['token_key'] not in session:
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
                db_session.add(User(name, email, session['user_id']))
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
            session[session['token_key']] = None
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
                return redirect(url_for('.edit_profile'))
    return render_template('edit_profile.html', form=form)

@auth.route('/_logout')
def logout():
    session.pop('user_id', None)
    session.pop(session.pop('token_key', None), None)
    flash(u'You were logged out.')
    return redirect(oid.get_next_url())
