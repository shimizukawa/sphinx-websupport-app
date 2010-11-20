# -*- coding: utf-8 -*-
"""
    sphinxweb build
    ~~~~~~~~~~~~~~~

    Script to build Sphinx docs for use with the webapp.

    :copyright: Copyright 2007-2010 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
import os

from flask import Flask

app = Flask(__name__)

app.config.from_envvar('SPHINXWEB_SETTINGS')

from sphinx.util import copy_static_entry
from sphinx.websupport import WebSupport

from sphinxweb.models import init_db

init_db()

support = WebSupport(srcdir=app.config['SOURCE_DIR'],
                     builddir=app.config['BUILD_DIR'],
                     search=app.config['SEARCH'],
                     storage=app.config['DATABASE_URI'])
support.build()

# copy resources from this webapp
for name in ['static', 'templates']:
    source_dir = os.path.join(os.getcwd(), 'sphinxweb', name)
    target_dir = os.path.join(app.config['BUILD_DIR'], name)
    copy_static_entry(source_dir, target_dir, None)
