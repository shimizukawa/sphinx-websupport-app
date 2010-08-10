from flask import Flask, g, session

from sphinxdemo import conf
from sphinxdemo.views.demo import demo
from sphinxdemo.views.auth import auth
from sphinxdemo.models import db_session, User

app = Flask(__name__)

app.config.update(
    DATABASE_URI = conf.DATABASE_URI,
    SECRET_KEY = conf.SECRET_KEY,
)

@app.before_request
def before_request():
    g.user = None
    if 'openid' in session:
        g.user = User.query.filter_by(openid=session['openid']).first()

@app.after_request
def after_request(response):
    db_session.remove()
    return response

app.register_module(demo)
app.register_module(auth)
