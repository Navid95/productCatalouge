import pytest

from app import create_app
from app import Test
from app.blueprints import BaseRestAPIById
from app.blueprints import BaseRestAPIByModelData
from app.extensions import db
from test.models.example import SingleParent
from test.models.example import SingleParentSchema


@pytest.fixture()
def app():
    app = create_app(__name__, Test)

    api_by_id = BaseRestAPIById.as_view(f"parent-single", model=SingleParent, schema=SingleParentSchema)
    api_by_model_data = BaseRestAPIByModelData.as_view(f"parent-group", model=SingleParent, schema=SingleParentSchema)
    app.add_url_rule(f"/parents/<uuid:id>", view_func=api_by_id)
    app.add_url_rule(f"/parents/", view_func=api_by_model_data)

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
