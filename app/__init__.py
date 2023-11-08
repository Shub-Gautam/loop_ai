from flask import Flask
from app.api import api_blueprint

app = Flask(__name__)

app.register_blueprint(api_blueprint)


