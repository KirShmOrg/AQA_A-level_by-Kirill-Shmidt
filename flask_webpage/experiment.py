from flask import Flask, render_template
from flask_bootstrap import Bootstrap, BOOTSTRAP_VERSION


app = Flask(__name__)
bootstrap = Bootstrap(app)
print(f'{BOOTSTRAP_VERSION = }')


@app.route('/<name>')
def index(name):
    return render_template('index.html', name=name)


@app.route('/base')
def base():
    return render_template('base.html')


if __name__ == '__main__':
    app.run(debug=True)
