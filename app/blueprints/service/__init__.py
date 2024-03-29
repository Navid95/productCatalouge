from uuid import UUID

from app.models import BaseModel


class BaseService:
    """
    Base service class that should contain applications business logics.

    Methods are considered general, for customizing the behaviour more methods should be developed. Exp create sub model, can be customized based on sub_model_key and each relationship gets it's own method.
    """

    def __init__(self, model: BaseModel):
        self.__model__ = model

    def get_model_by_id(self, model_id: UUID):
        model_object = self.__model__.get(model_id)
        if not model_object:
            return None
        return model_object

    def delete_model_by_id(self, model_id: UUID):
        return self.__model__.delete(model_id)

    def create_model(self, model_object: BaseModel):
        return self.__model__.post(model_object)

    def update_model(self, model_object: BaseModel):
        return self.__model__.put(model_object)

    def get_all_models(self, limit=10, page=1):
        return self.__model__.get_all(limit=limit, page=page)

    def get_sub_model(self, model_id: UUID, sub_model_key: str):
        model_object = self.__model__.get(model_id)
        sub_model_list = getattr(model_object, sub_model_key)
        return sub_model_list

    def create_sub_model(self, model_id: UUID, sub_model_list: list | BaseModel, sub_model_key: str,
                         many: bool = False):
        model = self.__model__.get(model_id)
        if many:
            sub_resources = list()
            for sub_resource_instance in sub_model_list:
                sub_resource = sub_resource_instance.get(sub_resource_instance.id)
                if sub_resource:
                    sub_resources.append(sub_resource)
            setattr(model, sub_model_key, sub_resources)
        else:
            sub_resource = sub_model_list.get(sub_model_list.id)
            if sub_resource:
                setattr(model, sub_model_key, sub_resource)

        put_result = self.__model__.put(model)
        return getattr(model, sub_model_key)

    def get_sub_model_by_id(self, model_id: UUID, sub_model_id: UUID, sub_model_key: str, many: bool = False):
        model = self.__model__.get(model_id)
        sub_resource_list = getattr(model, sub_model_key)
        if sub_resource_list:
            if many:
                for sub_model in sub_resource_list:
                    if sub_model_id == sub_model.id:
                        return sub_model
            else:
                if sub_resource_list.id == sub_model_id:
                    return sub_resource_list
        return None

    def delete_sub_model_by_id(self, model_id: UUID, sub_model_id: UUID, sub_model_key: str, many: bool = False):
        model = self.__model__.get(model_id)
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
                    return {'response': False}, 404
            else:
                if sub_resource_list.id == sub_model_id:
                    setattr(model, sub_model_key, None)
                else:
                    return {'response': False}, 404

            put_result = self.__model__.put(model)

            if put_result:
                return {'response': True}
            else:
                return {'response': False}, 400
        return {'response': False}, 400
