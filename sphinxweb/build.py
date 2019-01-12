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

app = Flask(__name__, instance_path=os.getcwd(), instance_relative_config=True)
app.config.from_envvar('SPHINXWEB_SETTINGS')

from sphinx.util import copy_static_entry
from sphinxcontrib.websupport import WebSupport

from .models import init_db


def main():
    init_db()

    support = WebSupport(srcdir=app.config['SOURCE_DIR'],
                         builddir=app.config['BUILD_DIR'],
                         search=app.config['SEARCH'],
                         storage=app.config['DATABASE_URI'])
    support.build()


if __name__ == '__main__':
    main()
