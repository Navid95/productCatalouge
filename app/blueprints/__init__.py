from uuid import UUID

from flask.views import MethodView
from flask import request
from marshmallow import ValidationError

from app.models import BaseModel
from app.models import BaseSchema


class BaseRestAPIById(MethodView):
    """
    Generic class of all REST APIs.

    For a given model of type BaseModel produces bellow http resource end points:
    GET , DELETE -> /models/id

    Is a child class of flask's MethodView.

    Class Variables:

    - init_every_request: If false instructs flask to use 1 instance for all incoming requests which is useful if the
    state of the object should be shared across requests, By-default it is False.

    """
    init_every_request = False

    def __init__(self, model: BaseModel, schema: BaseSchema):
        """
        Initiate the object.

        :param model: Model to use in methods.
        :param schema: Schema to use in serialization/deserialization.
        """
        self.__model__ = model
        self.__schema__ = schema

    def get(self, id: UUID):
        """
        HTTP GET, retrieve resource by given id.

        :param id: The id of the resource on DB.
        :return: Serialized presentation of the resource
        """
        schema = self.__schema__()
        model_object = self.__model__.get(id)
        if model_object:
            return schema.dump(model_object)
        else:
            return {}

    def delete(self, id: UUID):
        """
        HTTP DELETE, delete resource by given id.
        :param id: The id of the resource on DB.
        :return: bool
        """
        return {'response': self.__model__.delete(id)}


class BaseRestAPI(MethodView):
    """
    Generic class of all REST APIs.

    For a given model of type BaseModel produces bellow http resource end points:
    POST , PUT, GET -> /models/

    Is a child class of flask's MethodView.

    Class Variables:

    - init_every_request: If false instructs flask to use 1 instance for all incoming requests which is useful if the
    state of the object should be shared across requests, By-default it is False.

        """
    init_every_request = False

    def __init__(self, model: BaseModel, schema: BaseSchema):
        """
        Initiate the object.

        :param model: Model to use in methods.
        :param schema: Schema to use in serialization/deserialization.
        """
        self.__model__ = model
        self.__schema__ = schema

    def post(self):
        """
        HTTP POST, create the resource by given data in request body.
        :return: Serialized presentation of the resource
        """
        load_schema = self.__schema__(exclude=('id', 'created', 'updated', 'active'))
        dump_schema = self.__schema__()
        try:
            model_object = load_schema.load(request.json)
        except ValidationError as err:
            return err.messages
        return dump_schema.dump(self.__model__.post(model_object))

    def put(self):
        """
        HTTP PUT, update the resource by given data in request body.
        :return: Serialized presentation of the resource
        """
        load_schema = self.__schema__(exclude=('created', 'updated'))
        dump_schema = self.__schema__()
        try:
            model_object = load_schema.load(request.json)
        except ValidationError as err:
            return err.messages
        return dump_schema.dump(self.__model__.put(model_object))

    def get(self):
        """
        HTTP GET, retrieve all resources, 'limit' and 'page' URL parameters are used for pagination.

        note: limit and page default values are 10 and 1 respectively.

        :return: Serialized presentation of the resources
        """
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 10))
        except BaseException as err:
            print(err)
            page = 1
            limit = 10
        dump_schema = self.__schema__()
        return dump_schema.dump(self.__model__.get_all(limit=limit, page=page), many=True)


class BaseRestAPIRelationshipById(MethodView):
    init_every_request = False

    def __init__(self, model: BaseModel, relationship_schema: BaseSchema, relationship_key: str):
        self.__model__ = model
        self.__relationship_schema__ = relationship_schema
        self.__relationship_key__ = relationship_key

    def get(self, id: UUID):
        schema = self.__relationship_schema__()
        model = self.__model__.get(id)
        return schema.dump(getattr(model, self.__relationship_key__), many=True)

    # NODO develop put for relation under a top level resource

