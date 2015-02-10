# -*- coding: utf-8 -*-
"""
    sphinxweb runserver
    ~~~~~~~~~~~~~~~~~~~

    Script to run the sphinxweb test server.

    :copyright: Copyright 2007-2010 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
from . import app


def main():
    app.run()


if __name__ == '__main__':
    main()
