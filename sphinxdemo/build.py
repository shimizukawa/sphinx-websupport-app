
from sphinx.websupport import WebSupport

from sphinxdemo import conf
from sphinxdemo.models import init_db

init_db()

support = WebSupport(srcdir=conf.DOCTREE_ROOT,
                     outdir=conf.OUTPUT_DIR,
                     search=conf.SEARCH)
support.build()

