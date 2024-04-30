from uuid import UUID
from typing import Type

from flask import jsonify
from marshmallow  import ValidationError
from app.models import BaseModel
from app.models import BaseSchema


class BaseService:
    """
    Base service class that should contain applications business logics.

    Methods are considered general, for customizing the behaviour more methods should be developed. Exp create sub model, can be customized based on sub_model_key and each relationship gets it's own method.
    """

    def __init__(self, model: Type[BaseModel], schema: Type[BaseSchema],
                 relations: list[tuple[[BaseModel, Type[BaseSchema], str, [bool]]]] = None):
        self.__model__ = model
        self.__model_schema__ = schema
        self.__relation_models__ = dict()
        self.__relation_schemas__ = dict()
        self.__relation_many__ = dict()
        if relations:
            for relation in relations:
                self.__relation_models__[relation[2]] = relation[0]
                self.__relation_schemas__[relation[2]] = relation[1]
                self.__relation_many__[relation[2]] = relation[3]

    def get_model_by_id(self, model_id: UUID):
        model_object = self.__model__.get(model_id)
        if not model_object:
            return {}, 404
        dump_schema = self.__model_schema__()
        return dump_schema.dump(model_object)

    def delete_model_by_id(self, model_id: UUID):
        return {'result': self.__model__.delete(model_id)}

    def create_model(self, request_data: dict = None):
        load_schema = self.__model_schema__(exclude=('id', 'created', 'updated', 'active'))
        try:
            model_object = load_schema.load(request_data)
        except ValidationError as err:
            return jsonify(err.messages), 400
        dump_schema = self.__model_schema__()
        return dump_schema.dump(self.__model__.post(model_object))

    def update_model(self, request_data: dict = None):
        load_schema = self.__model_schema__(exclude=('created', 'updated'))
        try:
            model_object = load_schema.load(request_data)
        except ValidationError as err:
            return jsonify(err.messages), 400
        dump_schema = self.__model_schema__()
        return dump_schema.dump(self.__model__.put(model_object))

    def get_all_models(self, limit=10, page=1):
        dump_schema = self.__model_schema__()
        return dump_schema.dump(self.__model__.get_all(limit=limit, page=page), many=True)

    def get_sub_model(self, model_id: UUID, sub_model_key: str):
        dump_schema_class = self.__relation_schemas__.get(sub_model_key, None)
        if not dump_schema_class:
            return jsonify({
                'message': 'No schema found for the given resource'
            }), 500
        dump_schema = dump_schema_class()
        model = self.__model__.get(model_id)
        if not model:
            return jsonify({'message': f'{self.__model_schema__.__envelope__.get("single", "")} not found'}), 404
        sub_model_list = getattr(model, sub_model_key)
        return dump_schema.dump(sub_model_list, many=self.__relation_many__.get(sub_model_key, True))

    def create_sub_model(self, model_id: UUID, request_data: dict = None, sub_model_key: str = None):

        relation_schema_class = self.__relation_schemas__.get(sub_model_key, None)
        if not relation_schema_class:
            return jsonify({
                'message': 'No schema found for the given resource'
            }), 500

        many = self.__relation_many__.get(sub_model_key, False)
        dump_schema = relation_schema_class()
        load_schema = relation_schema_class(only=['id'], many=many)
        sub_resource_list = load_schema.load(request_data, many=many)

        model = self.__model__.get(model_id)
        if not model:
            return jsonify({'message': f'{self.__model_schema__.__envelope__.get("single", "")} not found'}), 404
        if many:
            sub_resources = list()
            for sub_resource_instance in sub_resource_list:
                sub_resource = sub_resource_instance.get(sub_resource_instance.id)
                if sub_resource:
                    sub_resources.append(sub_resource)
            setattr(model, sub_model_key, sub_resources)
        else:
            sub_resource = sub_resource_list.get(sub_resource_list.id)
            if sub_resource:
                setattr(model, sub_model_key, sub_resource)

        put_result = self.__model__.put(model)
        return dump_schema.dump(getattr(model, sub_model_key), many=many)

    def get_sub_model_by_id(self, model_id: UUID, sub_model_id: UUID, sub_model_key: str):
        many = self.__relation_many__.get(sub_model_key, False)
        model = self.__model__.get(model_id)
        if not model:
            return jsonify({'message': f'{self.__model_schema__.__envelope__.get("single", "")} not found'}), 404
        relation_schema_class = self.__relation_schemas__.get(sub_model_key, None)
        if not relation_schema_class:
            return jsonify({
                'message': 'No schema found for the given resource'
            }), 500
        dump_schema = relation_schema_class()
        sub_resource_list = getattr(model, sub_model_key)
        if sub_resource_list:
            if many:
                for sub_model in sub_resource_list:
                    if sub_model_id == sub_model.id:
                        return dump_schema.dump(sub_model, many)
            else:
                if sub_resource_list.id == sub_model_id:
                    return dump_schema.dump(sub_resource_list)
        return jsonify({
            'message': 'Not found'
        }), 400

    def delete_sub_model_by_id(self, model_id: UUID, sub_model_id: UUID, sub_model_key: str):
        many = self.__relation_many__.get(sub_model_key, False)
        model = self.__model__.get(model_id)
        if not model:
            return jsonify({'message': f'{self.__model_schema__.__envelope__.get("single", "")} not found'}), 404
        sub_resource_list = getattr(model, sub_model_key)
        if sub_resource_list:
            delete_result = False
            if many:
                for sub_model in sub_resource_list:
                    if sub_model.id == sub_model_id:
                        sub_resource_list.remove(sub_model)
                        delete_result = True
                        break
                if not delete_result:
                    return jsonify({'response': False}), 404
            else:
                if sub_resource_list.id == sub_model_id:
                    setattr(model, sub_model_key, None)
                else:
                    return jsonify({'response': False}), 404

            put_result = self.__model__.put(model)

            if put_result:
                return jsonify({'response': True})
            else:
                return jsonify({'response': False}), 400
        return jsonify({'response': False}), 400
