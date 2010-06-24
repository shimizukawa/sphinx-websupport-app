from flask import Flask, render_template, request
from sphinx.websupport import support

from sphinxdemo import conf

app = Flask(__name__)

support.init(srcdir=conf.DOCTREE_ROOT,
             outdir=conf.OUTPUT_DIR,
             search='xapian')

@app.route('/build')
def build():
    support.build()
    return 'Build Complete'

@app.route('/docs/')
@app.route('/docs/<path:docname>')
def doc(docname='contents'):
    document = support.get_document(docname)
    return render_template('doc.html', document=document)

@app.route('/docs/search')
def search():
    document = support.get_search_results(request.args.get('q', ''))
    return render_template('doc.html', document=document)

if __name__ == '__main__':
    app.run(debug=conf.DEBUG)
