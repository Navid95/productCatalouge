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


class BaseRestAPIRelationshipByModelId(MethodView):
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

    def __init__(self, model: BaseModel, sub_resource: BaseModel, sub_resource_schema: BaseSchema,
                 sub_resource_key: str, many: bool = True):
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
        self.__many__ = many

    def get(self, id: UUID):
        """
        HTTP GET, retrieve all sub-resources.

        note: getattr(model, self.__sub_resource_key__) is used!

        :param id: The id of the resource (model) on DB.
        :return: Serialized presentation of the sub-resources
        """
        schema = self.__sub_resource_schema__()
        model = self.__model__.get(id)
        return schema.dump(getattr(model, self.__sub_resource_key__), many=self.__many__)

    def put(self, id: UUID):
        """

        :param id:
        :return:
        """
        model = self.__model__.get(id)
        dump_schema = self.__sub_resource_schema__()
        load_schema = self.__sub_resource_schema__(only=['id'], many=self.__many__)
        sub_resource_list = load_schema.load(request.json, many=self.__many__)
        if self.__many__:
            sub_resources = list()
            for sub_resource_instance in sub_resource_list:
                sub_resource = self.__sub_resource__.get(sub_resource_instance.id)
                if sub_resource:
                    sub_resources.append(sub_resource)
            setattr(model, self.__sub_resource_key__, sub_resources)
        else:
            sub_resource = self.__sub_resource__.get(sub_resource_list)
            if sub_resource:
                setattr(model, self.__sub_resource_key__, sub_resource)

        put_result = self.__model__.put(model)

        return dump_schema.dump(getattr(model, self.__sub_resource_key__), many=self.__many__)


class BaseRestAPIRelationshipByModelIdBySubResourceId(MethodView):
    init_every_request = False

    def __init__(self, model: BaseModel, sub_resource: BaseModel, sub_resource_schema: BaseSchema,
                 sub_resource_key: str):
        self.__model__ = model
        self.__sub_resource__ = sub_resource
        self.__sub_resource_schema__ = sub_resource_schema
        self.__sub_resource_key__ = sub_resource_key

    def get(self, model_id: UUID, sub_resource_id: UUID):
        pass

    def delete(self, model_id: UUID, sub_resource_id: UUID):
        pass
