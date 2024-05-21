from typing import List
from uuid import UUID

from sqlalchemy import Table

from .. import BaseModel
from .. import BaseSchema

from app.extensions import db

product_category = Table(
    "product_category",
    BaseModel.metadata,
    db.Column("product_id", db.ForeignKey("product.id")),
    db.Column("category_id", db.ForeignKey("category.id")),
)


class Product(BaseModel):
    name: db.Mapped[str] = db.mapped_column(db.String, nullable=False)
    code: db.Mapped[str] = db.mapped_column(db.String, nullable=False, index=True)
    description: db.Mapped[str] = db.mapped_column(db.String)
    parent_id: db.Mapped[UUID] = db.mapped_column(db.ForeignKey('product.id'), nullable=True)
    parent: db.Mapped['Product'] = db.relationship(
        primaryjoin="and_(Product.id == Product.parent_id, Product.active)")
    categories: db.Mapped[List['Category']] = db.relationship(
        secondary=product_category,
        primaryjoin='and_(Product.id == product_category.c.product_id, Product.active)',
        secondaryjoin='and_(Category.id == product_category.c.category_id, Category.active)',
        back_populates='products'
    )


class Category(BaseModel):
    name: db.Mapped[str] = db.mapped_column(db.String, nullable=False, )
    code: db.Mapped[str] = db.mapped_column(db.String, nullable=False, index=True)
    description: db.Mapped[str] = db.mapped_column(db.String)

    products: db.Mapped[List[Product]] = db.relationship(
        secondary=product_category,
        primaryjoin='and_(Category.id == product_category.c.category_id, Category.active)',
        secondaryjoin='and_(Product.id == product_category.c.product_id, Product.active)',
        back_populates='categories'
    )


class CategorySchema(BaseSchema):
    __envelope__ = {'single': 'category', 'many': 'categories'}

    class Meta:
        model = Category
        include_fk = True


class ProductSchema(BaseSchema):
    __envelope__ = {'single': 'product', 'many': 'products'}

    class Meta:
        model = Product
        include_fk = True
