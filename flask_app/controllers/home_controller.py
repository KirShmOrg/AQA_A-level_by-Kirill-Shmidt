from flask import render_template, redirect, url_for

from flask_app import app
from flask_app.forms.cpu_search_form import CpuSearch


@app.route('/', methods=["GET", "POST"])
def index():
    form = CpuSearch()
    if form.validate_on_submit():
        cpu_name = form.cpu_name.data
        return redirect(url_for('show_cpu_page', cpu_name=cpu_name))
    return render_template('home/index.html', username='guest', cpu_search_form=form)


@app.route('/<username>')
def greet_user(username):
    return render_template('home/index.html', username=username)
