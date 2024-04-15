from flask_app import app
from flask import render_template


@app.route('/')
@app.route('/home')
@app.route('/index')
def index():
    return render_template('home/index.html')
