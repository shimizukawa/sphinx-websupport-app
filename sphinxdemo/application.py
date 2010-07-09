from flask import Flask, render_template, request, jsonify, abort
from sphinx.websupport import WebSupport

from sphinxdemo import conf

app = Flask(__name__)

support = WebSupport(srcdir=conf.DOCTREE_ROOT,
                     outdir=conf.OUTPUT_DIR,
                     search='xapian',
                     comments=True)

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

@app.route('/docs/get_comments')
def get_comments():
    parent_id = request.args.get('parent', '')
    comments = support.get_comments(parent_id)
    return jsonify(comments=comments)

@app.route('/docs/add_comment', methods=['POST'])
def add_comment():
    parent_id = request.form.get('parent', '')
    text = request.form.get('text', '')
    comment = support.add_comment(parent_id, text)
    return jsonify(comment=comment)

if __name__ == '__main__':
    app.run(debug=conf.DEBUG)
