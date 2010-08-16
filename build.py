# -*- coding: utf-8 -*-
"""
    sphinxdemo.build
    ~~~~~~~~~~~~~~~~

    Script to build Sphinx docs for use with the demo webapp.

    :copyright: Copyright 2007-2010 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
import os
import shutil

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

demo_static_dir = os.path.join(os.getcwd(), 'sphinxdemo', 'static')

static_dirs = ['_static', '_sources', '_images']

for directory in static_dirs:
    src = os.path.join(app.config['BUILD_DIR'], 'static', directory)
    dst = os.path.join(demo_static_dir, directory)
    if os.path.isdir(src):
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
