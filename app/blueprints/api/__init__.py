from uuid import UUID

from flask.views import MethodView
from flask import request
from marshmallow import ValidationError

from app.models import BaseModel
from app.models import BaseSchema
from app.blueprints.service import BaseService


class BaseAPI(MethodView):
    init_every_request = False
    __view_name_suffix__ = ''


class BaseRestAPIById(BaseAPI):
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
    __view_name_suffix__ = 'ById'

    def __init__(self, model: BaseModel, schema: BaseSchema, service: BaseService.__class__):
        """
        Initiate the object.

        :param model: Model to use in methods.
        :param schema: Schema to use in serialization/deserialization.
        :param service: service layer for business logic.
        """
        self.__model__ = model
        self.__schema__ = schema
        self.__service__ = service(self.__model__)

    def get(self, id: UUID):
        """
        HTTP GET, retrieve resource by given id.

        :param id: The id of the resource on DB.
        :return: Serialized presentation of the resource
        """
        schema = self.__schema__()
        model_object = self.__service__.get_model_by_id(id)
        if model_object:
            return schema.dump(model_object)
        else:
            return {}, 404

    def delete(self, id: UUID):
        """
        HTTP DELETE, delete resource by given id.
        :param id: The id of the resource on DB.
        :return: bool
        """
        return {'response': self.__service__.delete_model_by_id(id)}


class BaseRestAPI(BaseAPI):
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
    __view_name_suffix__ = ''

    def __init__(self, model: BaseModel, schema: BaseSchema, service: BaseService.__class__):
        """
        Initiate the object.

        :param model: Model to use in methods.
        :param schema: Schema to use in serialization/deserialization.
        """
        self.__model__ = model
        self.__schema__ = schema
        self.__service__ = service(model)

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
        return dump_schema.dump(self.__service__.create_model(model_object))

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
        return dump_schema.dump(self.__service__.update_model(model_object))

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
        return dump_schema.dump(self.__service__.get_all_models(limit=limit, page=page), many=True)


class BaseRestAPIRelationshipByModelId(BaseAPI):
    """
    Generic class of all REST APIs.

    For a given model of type BaseModel produces bellow http resource end points for its sub-resources:
    GET -> /models/id/sub-resources

    Is a child class of flask's MethodView.

    Class Variables:

    - init_every_request: If false instructs flask to use 1 instance for all incoming requests which is useful if the
    state of the object should be shared across requests, By-default it is False.
    """
    init_every_request = False
    __view_name_suffix__ = 'ByModelId'

    def __init__(self, model: BaseModel, sub_resource: BaseModel, sub_resource_schema: BaseSchema,
                 sub_resource_key: str, service: BaseService.__class__, many: bool = True):
        """
        Initiate the object.

        :param model: Model to use in methods.
        :param sub_resource: Sub-resource model to use in methods.
        :param sub_resource_schema: Schema to use in serialization/deserialization (sub-resources).
        :param sub_resource_key: The attribute name of the sub-resource on model (i.e model.key).
        :param many: Indicating if the relationship is with a single object or a collection of objects.
        """
        self.__model__ = model
        self.__sub_resource__ = sub_resource
        self.__sub_resource_schema__ = sub_resource_schema
        self.__sub_resource_key__ = sub_resource_key
        self.__service__ = service(model)
        self.__many__ = many

    def get(self, id: UUID):
        """
        HTTP GET, retrieve sub-resource(s).

        note: getattr(model, self.__sub_resource_key__) is used!

        :param id: The id of the resource (model) on DB.
        :return: Serialized presentation of the sub-resource(s)
        """
        schema = self.__sub_resource_schema__()
        return schema.dump(self.__service__.get_sub_model(id, self.__sub_resource_key__), many=self.__many__)

    def put(self, id: UUID):
        """
        HTTP PUT, update the subresource(s) by given data in request body.

        Based on the value of self.__many__ decides if it should operate on a single object or a collection of objects.
        note: setattr(model, self.__sub_resource_key__, sub_resources) is used!

        :param id: The id of the resource (model) on DB.
        :return: Serialized presentation of the sub-resource(s)
        """
        dump_schema = self.__sub_resource_schema__()
        load_schema = self.__sub_resource_schema__(only=['id'], many=self.__many__)
        sub_resource_list = load_schema.load(request.json, many=self.__many__)

        return dump_schema.dump(
            self.__service__.create_sub_model(id, sub_resource_list, self.__sub_resource_key__, self.__many__),
            many=self.__many__)


class BaseRestAPIRelationshipByModelIdBySubResourceId(BaseAPI):
    """
    Generic class of all REST APIs.

    For a given model of type BaseModel produces bellow http resource end points for its sub-resources:
    GET, DELETE -> /models/id/sub-resources/id

    Is a child class of flask's MethodView.

    Class Variables:

    - init_every_request: If false instructs flask to use 1 instance for all incoming requests which is useful if the
    state of the object should be shared across requests, By-default it is False.
    """
    init_every_request = False
    __view_name_suffix__ = 'ByModeIdBySubResourceId'

    def __init__(self, model: BaseModel, sub_resource: BaseModel, sub_resource_schema: BaseSchema,
                 sub_resource_key: str, service: BaseService.__class__, many: bool = True):
        self.__model__ = model
        self.__sub_resource__ = sub_resource
        self.__sub_resource_schema__ = sub_resource_schema
        self.__sub_resource_key__ = sub_resource_key
        self.__service__ = service(model)
        self.__many__ = many

    def get(self, model_id: UUID, sub_resource_id: UUID):
        """
        HTTP GET, retrieve a sub-resource under a resource.

        note: getattr(model, self.__sub_resource_key__) is used!

        :param model_id: The id of the resource (model) on DB.
        :param sub_resource_id: The id of the sub-resource on DB.
        :return: Serialized presentation of the sub-resource
        """
        dump_schema = self.__sub_resource_schema__()
        return dump_schema.dump(
            self.__service__.get_sub_model_by_id(model_id, sub_resource_id, self.__sub_resource_key__, self.__many__))

    def delete(self, model_id: UUID, sub_resource_id: UUID):
        """
        HTTP DELETE, delete a sub-resource under a resource.

        note: getattr(model, self.__sub_resource_key__) is used!

        :param model_id: The id of the resource (model) on DB.
        :param sub_resource_id: The id of the sub-resource on DB.
        :return: bool
        """
        return self.__service__.delete_sub_model_by_id(model_id, sub_resource_id, self.__sub_resource_key__,
                                                       self.__many__)
