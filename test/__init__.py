import pytest

from app import create_app
from app import Test
from app.blueprints import BaseRestAPI
from app.extensions import db
from test.models.example import SingleParent
from test.models.example import SingleParentSchema


@pytest.fixture()
def app():
    app = create_app(__name__, Test)

    api = BaseRestAPI.as_view(f"parent-item", model=SingleParent, schema=SingleParentSchema)
    app.add_url_rule(f"/parents/<uuid:id>", view_func=api)

    with app.app_context():
        db.create_all()
        # other setup can go here
        yield app

    with app.app_context():
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
