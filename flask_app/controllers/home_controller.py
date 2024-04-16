from flask import render_template

from flask_app import app
from flask_app.forms.cpu_search_form import CpuSearch


@app.route('/')
@app.route('/home')
@app.route('/index')
def index():
    return render_template('home/index.html', username='guest', cpu_search_form=CpuSearch())


@app.route('/<username>')
def greet_user(username):
    return render_template('home/index.html', username=username)
