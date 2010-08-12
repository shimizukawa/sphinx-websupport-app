from flask import Flask

app = Flask(__name__)

app.config.from_envvar('SPHINXDEMO_SETTINGS')

from sphinx.websupport import WebSupport

from sphinxdemo.models import init_db

init_db()

support = WebSupport(srcdir=app.config['SOURCE_DIR'],
                     builddir=app.config['BUILD_DIR'],
                     search=app.config['SEARCH'],
                     storage=app.config['DATABASE_URI'])
support.build()
