from flask import Blueprint

api1 = Blueprint('example_api_v1', __name__, url_prefix='/example/api/v1')


@api1.route('/test')
def for_test():
    return {'message': 'it\'s the first test'}
