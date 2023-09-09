from flask import Blueprint
from flask import request
from sqlalchemy.sql import select
from marshmallow import ValidationError

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
    product_variety1 = ProductVariety(product_id=product.id)
    product.varieties.append(product_variety)
    product.varieties.append(product_variety1)
    category = Category(name='ashghaaaal')
    product.categories.append(category)
    db.session.add(product_price)
    db.session.commit()
    return {
               'product': product_schema.dump(product),
           }, 201


@api1.route('/<uuid:product_id>')
def get_product_by_id(product_id):
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


@api1.route('/pricing/<uuid:id>')
def get_product_pricing_by_id(id):
    product_pricing = db.session.scalar(select(ProductPricing).where(ProductPricing.id == id))
    return product_pricing_schema.dump(product_pricing)


@api1.route('/varieties')
def get_product_variety_list():
    product_pricing = db.session.scalars(select(ProductPricing).order_by(ProductPricing.id))
    print(product_pricing)
    return {'pricings': [product_pricing_schema.dump(x) for x in product_pricing]}


@api1.route('/variety/<uuid:id>')
def get_product_variety_by_id(id):
    product_variety = db.session.scalar(select(ProductVariety).where(ProductVariety.id == id))
    return product_variety_schema.dump(product_variety)


@api1.route('/categories')
def get_product_category_list():
    categories = db.session.scalars(select(Category).order_by(Category.id))
    categories_schema = CategorySchema(many=True)
    return categories_schema.dump(categories)


@api1.route('/category/<uuid:id>')
def get_category_by_id(id):
    category = db.session.scalar(select(Category).where(Category.id == id))
    return category_schema.dump(category)


@api1.route('/category', methods=['POST'])
def load_test():
    # NODO 1000: create a decorator for deserialization
    # NODO 1000: create a decorator for serialization
    try:
        data = {
            "created": "2023-09-08T14:32:59.090028",
            "id": "08a558c4-b48f-420e-9d7b-8f9b3e33e314",
            "name": "ashghaaaal",
            "updated": "2023-09-08T14:32:59.090030"
        }
        product = product_schema.load(request.json)
        print(product)
        return product_schema.dump(product)
    except ValidationError as err:
        return err.messages
