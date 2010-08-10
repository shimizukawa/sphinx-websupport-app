
from sphinx.websupport import WebSupport

from sphinxdemo import conf
from sphinxdemo.models import init_db

init_db()

support = WebSupport(srcdir=conf.SOURCE_DIR,
                     builddir=conf.BUILD_DIR,
                     search=conf.SEARCH,
                     storage=conf.DATABASE_URI)
support.build()

