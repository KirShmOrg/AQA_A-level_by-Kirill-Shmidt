from flask import Flask
from flask_bootstrap import Bootstrap, BOOTSTRAP_VERSION


app = Flask(__name__)
bootstrap = Bootstrap(app)

from flask_app.controllers import home_controller, components_controller


if __name__ == '__main__':
    raise RuntimeError("This file should not be run")
