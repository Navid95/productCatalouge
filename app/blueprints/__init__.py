from uuid import UUID

from flask.views import MethodView
from flask import request
from marshmallow import ValidationError

from app.models import BaseModel
from app.models import BaseSchema


class BaseRestAPIById(MethodView):
    init_every_request = False

    def __init__(self, model: BaseModel, schema: BaseSchema):
        self.__model__ = model
        self.__schema__ = schema

    def get(self, id: UUID):
        schema = self.__schema__()
        return schema.dump(self.__model__.get(id))

    def delete(self, id: UUID):
        return {'response': self.__model__.delete(id)}


class BaseRestAPI(MethodView):
    init_every_request = False

    def __init__(self, model: BaseModel, schema: BaseSchema):
        self.__model__ = model
        self.__schema__ = schema

    def post(self):
        load_schema = self.__schema__(exclude=('id', 'created', 'updated', 'active'))
        dump_schema = self.__schema__()
        try:
            model_object = load_schema.load(request.json)
        except ValidationError as err:
            return err.messages
        return dump_schema.dump(self.__model__.post(model_object))

    def put(self):
        load_schema = self.__schema__(exclude=('created', 'updated'))
        dump_schema = self.__schema__()
        try:
            model_object = load_schema.load(request.json)
        except ValidationError as err:
            return err.messages
        return dump_schema.dump(self.__model__.put(model_object))

    def get(self):
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 10))
        except BaseException as err:
            print(err)
            page = 1
            limit = 10
        dump_schema = self.__schema__()
        return dump_schema.dump(self.__model__.get_all(limit=limit, page=page), many=True)

