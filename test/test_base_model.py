import uuid
import pytest

from marshmallow import EXCLUDE
from sqlalchemy.orm import InstanceState

from app import create_app, Test
from test.models.example import Example, ExampleSchema
from app.extensions import db, ma


@pytest.fixture()
def app():
    app = create_app(__name__, Test)

    with app.app_context():
        db.create_all()
        # other setup can go here
        yield app

    with app.app_context():
        db.drop_all()

    # clean up / reset resources here


def test_model_save(app):
    example = Example()
    Example.save(example)

    assert example.id
    assert not Example.save(example)
    assert not Example.save(list([1, 2, 3]))


def test_model_get(app):
    example1 = Example()
    Example.save(example1)
    example2 = Example.get(example1.id)

    assert example1 == example2


def test_model_patch(app):
    example1 = Example()
    Example.save(example1)
    updated_time1 = example1.updated
    Example.patch(example1.id, active=False)

    assert updated_time1 != example1.updated

    example1.blah = 'wow'

    assert not Example.patch(example1.id, blah='blah')


def test_model_put(app):
    example1 = Example()
    Example.save(example1)
    sample_text = f'test_model_put'
    example1.text = sample_text
    Example.put(example1)
    example2 = Example.get(example1.id)

    assert example1.updated == example2.updated
    assert example2.text == sample_text

    example2.id = None

    assert not Example.put(example2)


def test_model_delete(app):
    example1 = Example()
    Example.save(example1)
    id1 = example1.id
    Example.delete(id1)

    assert not Example.get(id1)
    assert not Example.delete(uuid.uuid4())


def test_model_to_json(app):
    example1 = Example()
    Example.save(example1)
    assert isinstance(example1.to_json(), dict)
    example2 = Example()
    assert isinstance(example2.to_json(), dict)


def test_schema_load(app):
    example1 = Example(text='blah')
    Example.save(example1)
    schema1 = ExampleSchema()
    example2 = schema1.load(data=example1.to_json(), unknown=EXCLUDE)
    assert example1.active == example2.active
