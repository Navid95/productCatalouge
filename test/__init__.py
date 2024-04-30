import pytest

from app import Test
from app import create_app
from app.models.log import IncomingAPI
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
from app.blueprints.service import BaseService
from app import register_api
from app import generate_view_name


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
                        'href': ma.URLFor(f'childrenById', values=dict(id='<id>')),
                        'rel': 'self',
                        'type': 'GET'
                    },
                    {
                        'href': ma.URLFor('childrenparentsByModelId', values=dict(id='<parent_id>')),
                        'rel': 'parent',
                        'type': 'GET'
                    }
                ],
                dump_only=True
            )
        }
    )
    register_api(app, SingleParent, SingleParentSchema, BaseService, [(Child, ChildAPISchema, 'children', True)])
    register_api(app, Child, ChildAPISchema, BaseService, [(SingleParent, SingleParentSchema, 'parent', True)])

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
