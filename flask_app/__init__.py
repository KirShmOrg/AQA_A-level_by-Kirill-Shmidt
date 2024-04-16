from flask import Flask
from flask_bootstrap import Bootstrap5

from config import Config


app = Flask(__name__)
app.config.from_object(Config())
bootstrap = Bootstrap5(app)

from flask_app.controllers import home_controller, components_controller


if __name__ == '__main__':
    print(f"{bootstrap.bootstrap_version = }")
    raise RuntimeError("This file should not be run")
