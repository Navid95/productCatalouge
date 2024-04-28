import logging
import os

from flask import Flask

from app.utilities.logging import configuration
from app.utilities.logging.api_log import log_api_call, get_request_time
from app import blueprints
from app.config import Development, Test, Production
from app.models import BaseSchema
from app.models import BaseModel
from app.models.product.product import Product
from app.models.product.product import ProductSchema
from app.models.product.product import Category
from app.models.product.product import CategorySchema
from app.models.log import IncomingAPI
from app.blueprints.api import BaseAPI
from app.blueprints.api import BaseRestAPI
from app.blueprints.api import BaseRestAPIById
from app.blueprints.api import BaseRestAPIRelationshipByModelId
from app.blueprints.api import BaseRestAPIRelationshipByModelIdBySubResourceId
from app.blueprints.service import BaseService
from app.extensions import db
from app.extensions import ma
from environ import APP_LOGGER_NAME

ENV = os.environ.get('FLASK_ENV', 'DEVELOP')
configurations = [Development, Test, Production]
logger = logging.getLogger(APP_LOGGER_NAME)


def create_app(name, config=Development):
    logger.info('initializing the flask app ...')
    app = Flask(import_name=name)
    app.config.from_object(config)
    app.config.from_pyfile('environ.py')
    app = register_extensions(app)
    app = register_blueprints(app)
    app = register_apis(app)
    app = register_app_hooks(app)
    return app


def register_blueprints(app):
    return app


def register_extensions(app):
    db.init_app(app)
    ma.init_app(app)
    return app


def register_apis(app):
    product_schema_ = ProductSchema.from_dict(
        {
            'links': ma.Hyperlinks(
                [
                    {
                        'href': ma.URLFor(f'productsById', values=dict(id='<id>')),
                        'rel': 'self',
                        'type': 'GET'
                    },
                    {
                        'href': ma.URLFor('productscategoriesByModelId', values=dict(id='<id>')),
                        'rel': 'parent',
                        'type': 'GET'
                    }
                ],
                dump_only=True
            )
        }
    )

    category_schema_ = CategorySchema.from_dict(
        {
            'links': ma.Hyperlinks(
                [
                    {
                        'href': ma.URLFor(f'categoriesById', values=dict(id='<id>')),
                        'rel': 'self',
                        'type': 'GET'
                    },
                    {
                        'href': ma.URLFor(f'categoriesproductsByModelId', values=dict(id='<id>')),
                        'rel': 'products',
                        'type': 'GET'
                    }
                ],
                dump_only=True
            )
        }
    )
    register_api(app, Product, product_schema_, BaseService, [(Category, CategorySchema, 'categories', True)])
    register_api(app, Category, category_schema_, BaseService, [(Product, ProductSchema, 'products', True)])

    return app


def register_api(app: Flask, resource: BaseModel, resource_schema: BaseSchema, service: BaseService,
                 relations: list[tuple[[BaseModel, BaseSchema, str, [bool]]]] = None):
    rest_api = BaseRestAPI.as_view(
        name=f'{generate_view_name(BaseRestAPI, resource_schema)}',
        model=resource,
        schema=resource_schema,
        service=service
    )

    rest_api_by_id = BaseRestAPIById.as_view(
        name=f'{generate_view_name(BaseRestAPIById, resource_schema)}',
        model=resource,
        schema=resource_schema,
        service=service
    )

    app.add_url_rule(generate_view_uri(BaseRestAPI, resource_schema), view_func=rest_api)
    app.add_url_rule(generate_view_uri(BaseRestAPIById, resource_schema), view_func=rest_api_by_id)

    if relations:
        for relation in relations:
            api_relationship = BaseRestAPIRelationshipByModelId.as_view(
                name=generate_view_name(BaseRestAPIRelationshipByModelId, resource_schema, relation),
                model=resource,
                sub_resource=relation[0],
                sub_resource_schema=relation[1],
                sub_resource_key=relation[2],
                many=relation[3],
                service=service
            )

            api_relationship_by_id = BaseRestAPIRelationshipByModelIdBySubResourceId.as_view(
                name=generate_view_name(BaseRestAPIRelationshipByModelIdBySubResourceId, resource_schema, relation),
                model=resource,
                sub_resource=relation[0],
                sub_resource_schema=relation[1],
                sub_resource_key=relation[2],
                many=relation[3],
                service=service
            )

            app.add_url_rule(generate_view_uri(BaseRestAPIRelationshipByModelId, resource_schema, relation),
                             view_func=api_relationship)
            app.add_url_rule(generate_view_uri(BaseRestAPIRelationshipByModelIdBySubResourceId, resource_schema, relation),
                             view_func=api_relationship_by_id)

    return app


def generate_view_name(end_point: BaseAPI, resource_schema: BaseSchema,
                       relation: tuple[[BaseModel, BaseSchema, str, bool]] = None) -> str:
    view_name = resource_schema.__envelope__.get("many")

    if relation:
        view_name = view_name + relation[1].__envelope__.get("many") + end_point.__view_name_suffix__
    else:
        view_name = view_name + end_point.__view_name_suffix__

    return view_name


def generate_view_uri(end_point: BaseAPI, resource_schema: BaseSchema,
                      relation: tuple[[BaseModel, BaseSchema, str, bool]] = None) -> str:
    view_uri = '/' + resource_schema.__envelope__.get("many")

    if end_point is BaseRestAPI:
        return view_uri
    elif end_point is BaseRestAPIById:
        return view_uri + '/' + '<uuid:id>'
    elif relation:
        if end_point is BaseRestAPIRelationshipByModelId:
            return view_uri + '/' + '<uuid:id>' + '/' + relation[1].__envelope__.get("many")
        elif end_point is BaseRestAPIRelationshipByModelIdBySubResourceId:
            return view_uri + '/' + '<uuid:model_id>' + '/' + relation[1].__envelope__.get(
                "many") + '/' + '<uuid:sub_resource_id>'
    return ''


def register_app_hooks(app):
    hook1 = app.before_request(get_request_time)
    hook2 = app.after_request(log_api_call)
    return app
