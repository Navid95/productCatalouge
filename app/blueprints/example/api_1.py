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
    return {
               'product': product_schema.dump(product),
           }, 201


@api1.route('/<uuid:product_id>')
def get_product_by_id(product_id):
    # product = db.session.execute(select(Product).where(Product.id == product_id)).first()[0]
    # NODO remember either use UUID(str - default) or uuid: blah in URL
    product = db.session.scalar(select(Product).where(Product.id == product_id))
    return product_schema.dump(product)


@api1.route('/list')
def get_product_list():
    products = db.session.scalars(select(Product).order_by(Product.id))

    return product_schema.dump(products)


@api1.route('/pricings')
def get_product_pricing_list():
    product_pricing = db.session.scalars(select(ProductPricing).order_by(ProductPricing.id))
    print(product_pricing)
    return {'pricings': [product_pricing_schema.dump(x) for x in product_pricing]}


@api1.route('/varieties')
def get_product_variety_list():
    product_pricing = db.session.scalars(select(ProductPricing).order_by(ProductPricing.id))
    print(product_pricing)
    return {'pricings': [product_pricing_schema.dump(x) for x in product_pricing]}


@api1.route('/variety/<uuid:id>')
def get_product_variety_by_id(id):
    product_variety = db.session.scalar(select(ProductVariety).where(ProductVariety.id == id))
    return product_variety_schema.dump(product_variety)
