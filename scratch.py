from flask import Flask, render_template, request, redirect
from flask.helpers import url_for

from models import *

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    data = {
        'posts': Post.select()
    }
    return render_template('index.html')

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if request.method == 'POST':
        Post.create(markdown=request.form['editor'])
        return redirect(url_for('index'))
    return render_template('edit.html')

if __name__ == '__main__':
    app.debug = True
    app.run()