from typing import List
from uuid import UUID

from app.extensions import db
from app.extensions import ma
from . import BaseModel


class Product(BaseModel):
    name: db.Mapped[str] = db.mapped_column()

    varieties: db.Mapped[List['ProductVariety']] = db.relationship(back_populates='product')  # one-to-many
    pricing: db.Mapped['ProductPricing'] = db.relationship(back_populates='product')  # one-to-one


class ProductPricing(BaseModel):
    product_id: db.Mapped[UUID] = db.mapped_column(db.ForeignKey("product.id"))
    product: db.Mapped[Product] = db.relationship(back_populates='pricing')


class ProductVariety(BaseModel):
    product_id: db.Mapped[UUID] = db.mapped_column(db.ForeignKey("product.id"))
    product: db.Mapped['Product'] = db.relationship(back_populates='varieties')


# Marshmallow schemas

class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        # fields = ("id", "name", "created", "updated", "_links")
        model = Product
        # include_fk = True

    varieties = ma.List(ma.HyperlinkRelated("example_api_v1.get_product_variety_by_id"))
    # id = ma.auto_field()
    # name = ma.auto_field()

    # _links = ma.Hyperlinks(
    #     {
    #         "self": ma.URLFor("example_api_v1.get_product_by_id", values=dict(product_id="<id>")),
    #     }
    # )


product_schema = ProductSchema()


class ProductPricingSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ProductPricing
        # include_fk = True

    product = ma.HyperlinkRelated("example_api_v1.get_product_by_id", url_key='product_id')


product_pricing_schema = ProductPricingSchema()


class ProductVarietySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ProductVariety
        # include_fk = True

    product = ma.HyperlinkRelated("example_api_v1.get_product_by_id", url_key='product_id')


product_variety_schema = ProductVarietySchema()
