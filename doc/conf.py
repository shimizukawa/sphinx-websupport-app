# -*- coding: utf-8 -*-
extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
source_parsers = {'.md': 'recommonmark.parser.CommonMarkParser',}
source_suffix = ['.rst', '.md']
master_doc = 'index'

project = u'Sphinx Demo Webapp'
copyright = u'2010, Sphinx Team'
version = release = '0.1'
exclude_trees = ['_build']
pygments_style = 'sphinx'
html_theme = 'default'


# -- Options for WebApp --------------------------------------------------------
# configuration options for Xapian:
xapian_db = 'xapian_db'
reporoot = 'repo'
repodir = 'doc'
reposums = 'reposums.pkl'
piddbfile = 'piddb.pkl'
licence = 'BSD'

