from flask import Flask, g, session

app = Flask(__name__)
app.config.from_envvar('SPHINXDEMO_SETTINGS')
app.root_path = app.config['BUILD_DIR']

from sphinxdemo.models import db_session, User

@app.before_request
def before_request():
    g.user = None
    if 'openid' in session:
        g.user = User.query.filter_by(openid=session['openid']).first()

@app.after_request
def after_request(response):
    db_session.remove()
    return response

from sphinxdemo.views.demo import demo
from sphinxdemo.views.auth import auth
app.register_module(demo)
app.register_module(auth)
