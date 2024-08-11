from flask import Flask
from app import initiate_app


def create_app():
    app = Flask(__name__)
    initiate_app(app)
    return app

