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
@app.route('/index')
def index():
    data = {
        'posts': Post.select().order_by(Post.created_at.desc())
    }
    return render_template('index.html', **data)

@app.route('/edit', methods=['GET', 'POST'], endpoint='new-post')
@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit(post_id=None):
    data = {'post': None}

    if post_id is None:
        p = Post()
    else:
        p = Post.get(Post.id == post_id)
        data['post'] = p

    if request.method == 'POST':
        text_markdown = request.form['editor']
        tags = request.form['tags'].split(',')

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

        for tag in tags:
            t, created = Tag.get_or_create(name=tag)
            TagPost.get_or_create(post_id=p.id, tag_id=t.id)

        return redirect(url_for('index'))

    return render_template('edit.html', **data)

@app.route('/new', methods=['GET', 'POST'])
def new():
    data = {
        'new_post': True,
        'post': {},
    }
    return render_template('edit.html', **data)

@app.route('/delete/<int:post_id>')
def delete(post_id):
    pass

if app.debug:
    @app.route('/media/<path:filename>')
    def media(filename):
        for char in ',/': filename = filename.strip(char)
        return send_from_directory(app.root_path + '/media', filename)

if __name__ == '__main__':
    app.run()