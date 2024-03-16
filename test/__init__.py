import pytest

from app import Test
from app import create_app
from app.blueprints.api import BaseRestAPIById
from app.blueprints.api import BaseRestAPI
from app.blueprints.api import BaseRestAPIRelationshipByModelId
from app.blueprints.api import BaseRestAPIRelationshipByModelIdBySubResourceId
from app.extensions import db
from app.extensions import ma
from test.models.example import SingleParent
from test.models.example import SingleParentSchema
from test.models.example import Child
from test.models.example import ChildSchema
from app.blueprints import BaseService


@pytest.fixture()
def app():
    app = create_app(__name__, Test)

    """
    Sample for generating Schemas
    """
    ChildAPISchema = ChildSchema.from_dict(
        {
            'links': ma.Hyperlinks(
                [
                    {
                        'href': ma.URLFor(f'child-single', values=dict(id='<id>')),
                        'rel': 'self',
                        'type': 'GET'
                    },
                    {
                        'href': ma.URLFor('parent-single', values=dict(id='<parent_id>')),
                        'rel': 'parent',
                        'type': 'GET'
                    }
                ],
                dump_only=True
            )
        }
    )

    api_by_id = BaseRestAPIById.as_view(f"parent-single", model=SingleParent, schema=SingleParentSchema,
                                        service=BaseService)
    api = BaseRestAPI.as_view(f"parent-group", model=SingleParent, schema=SingleParentSchema, service=BaseService)
    app.add_url_rule(f"/parents/<uuid:id>", view_func=api_by_id)
    app.add_url_rule(f"/parents", view_func=api)

    children_by_id = BaseRestAPIById.as_view(f'child-single', model=Child, schema=ChildAPISchema, service=BaseService)
    children = BaseRestAPI.as_view(f'child-base', model=Child, schema=ChildAPISchema, service=BaseService)
    app.add_url_rule(f"/children/<uuid:id>", view_func=children_by_id)
    app.add_url_rule(f"/children", view_func=children)

    parent_children = BaseRestAPIRelationshipByModelId.as_view(f'parent-children', model=SingleParent,
                                                               sub_resource=Child,
                                                               sub_resource_schema=ChildAPISchema,
                                                               sub_resource_key='children',
                                                               service=BaseService)
    app.add_url_rule(f'/parents/<uuid:id>/children', view_func=parent_children)

    parent_children_id = BaseRestAPIRelationshipByModelIdBySubResourceId.as_view(f'parent-children-id',
                                                                                 model=SingleParent,
                                                                                 sub_resource=Child,
                                                                                 sub_resource_schema=ChildAPISchema,
                                                                                 sub_resource_key='children',
                                                                                 service=BaseService)

    app.add_url_rule(f'/parents/<uuid:model_id>/children/<uuid:sub_resource_id>', view_func=parent_children_id)

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
