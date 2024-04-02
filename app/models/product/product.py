from .. import BaseModel
from .. import BaseSchema

from app.extensions import db


class Product(BaseModel):
    name: db.Mapped[str] = db.mapped_column(db.String)


class ProductSchema(BaseSchema):
    __envelope__ = {'single': 'product', 'many': 'products'}

    class Meta:
        model = Product
