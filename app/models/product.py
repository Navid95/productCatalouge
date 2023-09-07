from typing import List
from uuid import UUID

from app.extensions import db
from . import BaseModel


class Product(BaseModel):
    name: db.Mapped[str] = db.mapped_column()

    varieties: db.Mapped[List['ProductVariety']] = db.relationship()  # one-to-many
    pricing: db.Mapped['ProductPricing'] = db.relationship()    # one-to-one

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'varieties': [v.json() for v in self.varieties],
            'pricing': self.pricing.json()
        }


class ProductPricing(BaseModel):
    product_id: db.Mapped[UUID] = db.mapped_column(db.ForeignKey("product.id"))

    def json(self):
        return {
            'id': self.id,
            'product_id': self.product_id
        }


class ProductVariety(BaseModel):
    product_id: db.Mapped[UUID] = db.mapped_column(db.ForeignKey("product.id"))

    # product: db.Mapped['Product'] = db.relationship(back_populates='varieties')

    def json(self):
        return {
            'id': self.id,
            'product_id': self.product_id
        }
