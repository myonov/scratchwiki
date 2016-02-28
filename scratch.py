from flask import Flask, render_template, request, redirect
from flask.helpers import url_for, send_from_directory
import markdown

from models import *

app = Flask(__name__)
app.debug = True

@app.template_filter('date')
def _pretty_date(value):
    return value.strftime('%H:%M:%S %d.%m.%Y')

@app.route('/')
def index():
    tags = request.args.get('tags', '')
    tags = tags.split(',')
    if len(tags) == 1 and tags[0] == '':
        tags = []

    current_page = int(request.args.get('page', 1))
    pager = Pager(Post.relevant_posts(tags), current_page)

    data = {
        'pager': pager,
        'tags': tags,
    }
    return render_template('index.html', **data)

@app.route('/edit', methods=['GET', 'POST'], endpoint='new-post')
@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit(post_id=None):
    data = {'post': None, 'new_tags': []}

    if post_id is None:
        p = Post()
    else:
        p = Post.get(Post.id == post_id)
        data['post'] = p

    if request.method == 'POST':
        text_markdown = request.form['editor']
        tags = request.form['tags'].split(',')

        if len(tags) == 1 and tags[0] == '':
            tags = []

        text_html = markdown.markdown(
            text_markdown,
            extensions=[
                'markdown.extensions.fenced_code',
                'markdown.extensions.tables',
            ],
        )

        p.markdown = text_markdown
        p.html = text_html
        p.save()
        p.update_tags(tags)

        return redirect(url_for('index'))

    return render_template('edit.html', **data)

@app.route('/new', methods=['GET', 'POST'])
def new():
    p = Post()
    p.markdown = ''
    data = {
        'new_post': True,
        'new_tags': request.args.get('tags'),
        'post': p,
    }
    return render_template('edit.html', **data)

@app.route('/delete/<int:post_id>')
def delete(post_id):
    Post.get(Post.id == post_id).remove()
    return redirect(request.referrer or url_for('index'))

@app.route('/post/<int:post_id>')
def post(post_id):
    data = {
        'post': Post.get(Post.id == post_id)
    }
    return render_template('post.html', **data)

if app.debug:
    @app.route('/media/<path:filename>')
    def media(filename):
        for char in ',/': filename = filename.strip(char)
        return send_from_directory(app.root_path + '/media', filename)

if __name__ == '__main__':
    app.run()