from uuid import UUID

from flask.views import MethodView

from app.models import BaseModel
from app.models import BaseSchema


class BaseRestAPI(MethodView):
    init_every_request = False

    def __init__(self, model: BaseModel, schema: BaseSchema):
        self.__model__ = model
        self.__schema__ = schema

    def get(self, id: UUID):
        schema = self.__schema__()
        return schema.dump(self.__model__.get(id))
