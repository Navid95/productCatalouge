from flask import Blueprint
from sqlalchemy.sql import select

from app.models.product import *
from app.extensions import db

api1 = Blueprint('example_api_v1', __name__, url_prefix='/product/api/v1')


@api1.route('/test')
def for_test():
    product = Product(name='product')
    db.session.add(product)
    db.session.flush()
    product_price = ProductPricing(product_id=product.id)
    product_variety = ProductVariety(product_id=product.id)
    product.varieties.append(product_variety)
    db.session.add(product_price)
    db.session.commit()
    print(f'product: {product.json()}')
    print(f'product_price: {product_price.json()}')
    print(f'product_variety: {product_variety.json()}')
    return {
               'product': product.json(),
               'product_price': product_price.json(),
               'product_variety': product_variety.json()
           }, 201


@api1.route('/<product_id>')
def get_product_by_id(product_id: int):
    # product = db.session.execute(select(Product).where(Product.id == product_id)).first()[0]
    product = db.session.scalar(select(Product).where(Product.id == product_id))
    print(product.__class__)
    return product.json()


@api1.route('/list')
def get_product_list():
    products = db.session.scalars(select(Product).order_by(Product.id))

    return {
        'products': [p.json() for p in products]
    }
