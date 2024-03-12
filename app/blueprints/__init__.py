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
