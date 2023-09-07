import os
from app.config import Development, Test, Production
from flask import Flask
from app import blueprints
from app.extensions import db
from app.models.product import Product

ENV = os.environ.get('FLASK_ENV', 'DEVELOP')
configurations = [Development, Test, Production]


def create_app(name, config=Development):
    app = Flask(import_name=name)
    app.config.from_object(config)
    app.config.from_pyfile('environ.py')
    app = register_extensions(app)
    app = register_blueprints(app)
    return app


def register_blueprints(app):
    app.register_blueprint(blueprints.api1)
    return app


def register_extensions(app):
    db.init_app(app)
    return app
