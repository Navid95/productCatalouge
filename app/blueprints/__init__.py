from uuid import UUID

from app.models import BaseModel


class BaseService:
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

    def create_sub_model(self, model_id: UUID, sub_resource_list: list | BaseModel, sub_resource_key: str,
                         many: bool = False):
        model = self.__model__.get(model_id)
        if many:
            sub_resources = list()
            for sub_resource_instance in sub_resource_list:
                sub_resource = sub_resource_instance.get(sub_resource_instance.id)
                if sub_resource:
                    sub_resources.append(sub_resource)
            setattr(model, sub_resource_key, sub_resources)
        else:
            sub_resource = sub_resource_list.get(sub_resource_list.id)
            if sub_resource:
                setattr(model, sub_resource_key, sub_resource)

        put_result = self.__model__.put(model)
        return getattr(model, sub_resource_key)
