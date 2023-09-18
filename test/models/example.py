from app.models import BaseModel, BaseSchema
from app.extensions import db


class Example(BaseModel):
    text: db.Mapped[str] = db.mapped_column(nullable=True)


class ExampleSchema(BaseSchema):
    class Meta:
        model = Example
