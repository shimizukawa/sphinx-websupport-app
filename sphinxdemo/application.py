from flask import Flask, render_template
from sphinx.websupport import support

from sphinxdemo import conf

app = Flask(__name__)

# Template that will be used to render comments on the page.
comment_html = """
<a href="#" onclick="alert('[ comment stub &lt;{{ id }}&gt; ]');">comment</a>
"""
support.init(srcdir=conf.DOCTREE_ROOT,
             outdir=conf.OUTPUT_DIR,
             comment_html=comment_html)


@app.route('/build')
def build():
    support.build()
    return 'Build Complete'


@app.route('/docs/')
@app.route('/docs/<docname>')
def doc(docname='contents'):
    document = support.get_document(docname)
    return render_template('doc.html', document=document)

if __name__ == '__main__':
    app.run(debug=conf.DEBUG)
