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
from sphinx.websupport import WebSupport

from .models import init_db


class ReCommonMarkTraversableWrapper(object):
    """
    patch for node.rawsource empty problem
    """
    def __init__(self, doctree):
        self.doctree = doctree

    def traverse(self, condition, *args, **kw):
        for n in self.doctree.traverse(condition, *args, **kw):
            if not n.rawsource:
                n.rawsource = n.astext()
            yield n


class DummyTraversable(object):
    def __init__(self, iterable):
        self.iterable = iterable

    def traverse(self, condition, *args, **kw):
        for n in self.iterable:
            yield DummyNode(uid=n.id, rawsource=n.source)


class DummyNode(object):
    def __init__(self, uid, rawsource):
        self.uid = uid
        self.rawsource = rawsource


def add_uids(doctree, condition):
    from sphinx.util import SEP
    from sphinx.websupport.storage.sqlalchemy_db import Node
    from sphinx import versioning
    from .models import db_session

    srcdir = app.config['SOURCE_DIR']
    source = doctree['source']
    docname = os.path.splitext(os.path.relpath(source, srcdir).replace(os.path.sep, SEP))[0]

    q = db_session().query(Node).filter(Node.document==docname)
    return versioning.merge_doctrees(
        DummyTraversable(q), ReCommonMarkTraversableWrapper(doctree), condition)


def patch_to_sphinx():
    import sphinx.versioning
    import sphinx.environment
    sphinx.versioning.add_uids = add_uids
    sphinx.environment.add_uids = add_uids


def main():
    patch_to_sphinx()
    init_db()

    support = WebSupport(srcdir=app.config['SOURCE_DIR'],
                         builddir=app.config['BUILD_DIR'],
                         search=app.config['SEARCH'],
                         storage=app.config['DATABASE_URI'])
    support.build()


if __name__ == '__main__':
    main()
