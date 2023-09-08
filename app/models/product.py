from typing import List
from uuid import UUID

from sqlalchemy import Table
from marshmallow import post_load

from app.extensions import db
from app.extensions import ma
from . import BaseModel
from . import BaseSchema

print(BaseModel.metadata)

product_categories = Table(
    "product_categories",
    BaseModel.metadata,
    db.Column("product_id", db.ForeignKey("product.id")),
    db.Column("category_id", db.ForeignKey("category.id")),
)


class Product(BaseModel):
    name: db.Mapped[str] = db.mapped_column()

    varieties: db.Mapped[List['ProductVariety']] = db.relationship(back_populates='product')  # one-to-many
    pricing: db.Mapped['ProductPricing'] = db.relationship(back_populates='product')  # one-to-one
    categories: db.Mapped[List['Category']] = db.relationship(secondary=product_categories,
                                                              back_populates='products')  # many-to-many


class ProductPricing(BaseModel):
    product_id: db.Mapped[UUID] = db.mapped_column(db.ForeignKey("product.id"))
    product: db.Mapped[Product] = db.relationship(back_populates='pricing')


class ProductVariety(BaseModel):
    product_id: db.Mapped[UUID] = db.mapped_column(db.ForeignKey("product.id"))
    product: db.Mapped['Product'] = db.relationship(back_populates='varieties')


class Category(BaseModel):
    name: db.Mapped[str] = db.mapped_column()

    products: db.Mapped[List['Product']] = db.relationship(secondary=product_categories, back_populates='categories')


# Marshmallow schemas

class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product

    varieties = ma.List(ma.HyperlinkRelated("example_api_v1.get_product_variety_by_id"))
    pricing = ma.HyperlinkRelated("example_api_v1.get_product_pricing_by_id")
    categories = ma.List(ma.HyperlinkRelated("example_api_v1.get_category_by_id"))


product_schema = ProductSchema()


class ProductPricingSchema(BaseSchema):
    class Meta:
        model = ProductPricing
        # include_fk = True

    product = ma.HyperlinkRelated("example_api_v1.get_product_by_id", url_key='product_id')


product_pricing_schema = ProductPricingSchema()


class ProductVarietySchema(BaseSchema):
    class Meta:
        model = ProductVariety

    product = ma.HyperlinkRelated("example_api_v1.get_product_by_id", url_key='product_id')


product_variety_schema = ProductVarietySchema()


class CategorySchema(BaseSchema):
    class Meta:
        model = Category

    products = ma.List(ma.HyperlinkRelated("example_api_v1.get_product_by_id", url_key='product_id'))


category_schema = CategorySchema()
