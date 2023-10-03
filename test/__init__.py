import pytest

from app import create_app
from app import Test
from app.blueprints import BaseRestAPIById
from app.blueprints import BaseRestAPI
from app.blueprints import BaseRestAPIRelationshipById
from app.extensions import db
from test.models.example import SingleParent
from test.models.example import SingleParentSchema
from test.models.example import Child
from test.models.example import ChildSchema


@pytest.fixture()
def app():
    app = create_app(__name__, Test)

    api_by_id = BaseRestAPIById.as_view(f"parent-single", model=SingleParent, schema=SingleParentSchema)
    api = BaseRestAPI.as_view(f"parent-group", model=SingleParent, schema=SingleParentSchema)
    app.add_url_rule(f"/parents/<uuid:id>", view_func=api_by_id)
    app.add_url_rule(f"/parents", view_func=api)

    children_by_id = BaseRestAPIById.as_view(f'child-single', model=Child, schema=ChildSchema)
    children = BaseRestAPI.as_view(f'child-base', model=Child, schema=ChildSchema)
    app.add_url_rule(f"/children/<uuid:id>", view_func=children_by_id)
    app.add_url_rule(f"/children", view_func=children)

    parent_children = BaseRestAPIRelationshipById.as_view(f'parent-children', model=SingleParent,
                                                          relationship_schema=ChildSchema, relationship_key='children')
    app.add_url_rule(f'/parents/<uuid:id>/children', view_func=parent_children)

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
