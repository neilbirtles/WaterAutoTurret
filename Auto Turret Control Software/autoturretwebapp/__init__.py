from flask import Flask
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_pyfile('appconfig.cfg')

from autoturretwebapp import routes

bootstrap = Bootstrap(app)