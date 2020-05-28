from flask import Flask
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm

app = Flask(__name__)
bootstrap = Bootstrap(app)

from app import routes