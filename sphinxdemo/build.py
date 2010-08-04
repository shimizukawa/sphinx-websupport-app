
from sphinx.websupport import WebSupport

from sphinxdemo import conf

support = WebSupport(srcdir=conf.DOCTREE_ROOT,
                     outdir=conf.OUTPUT_DIR,
                     search=conf.SEARCH)
support.build()

