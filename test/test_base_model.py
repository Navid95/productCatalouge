import uuid
import pytest

from marshmallow import EXCLUDE

from app import create_app, Test
from test.models.example import SingleParent, ParentSchema, Child
from app.extensions import db


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
    parent = SingleParent(name='parent1')

    assert SingleParent.save(parent)
    assert parent.id
    assert not SingleParent.save(parent)
    assert not SingleParent.save(list([1, 2, 3]))


def test_model_get(app):
    parent1 = SingleParent(name='parent1')

    assert SingleParent.save(parent1)

    parent2 = SingleParent.get(parent1.id)

    assert parent1 == parent2


def test_model_patch(app):
    parent1 = SingleParent(name='parent1')

    assert SingleParent.save(parent1)

    updated_time1 = parent1.updated

    assert SingleParent.patch(parent1.id, name='parent1 edited')
    assert updated_time1 != parent1.updated

    parent1.blah = 'wow'

    assert SingleParent.patch(parent1.id, blah='blah')

    parent2 = SingleParent.get(parent1.id)

    assert hasattr(parent2, 'blah')


def test_model_put(app):
    parent1 = SingleParent(name='parent1')

    assert SingleParent.save(parent1)

    sample_text = f'test_model_put'
    parent1.name = sample_text

    assert SingleParent.put(parent1)

    parent2 = SingleParent.get(parent1.id)

    assert parent2
    assert parent1.updated == parent2.updated
    assert parent2.name == sample_text


def test_model_delete(app):
    parent1 = SingleParent(name='parent1')

    assert SingleParent.save(parent1)

    id1 = parent1.id

    assert SingleParent.delete(id1)
    assert not SingleParent.get(id1)
    assert not SingleParent.delete(uuid.uuid4())


def test_model_to_json(app):
    parent1 = SingleParent(name='parent1')

    assert SingleParent.save(parent1)
    assert isinstance(parent1.to_json(), dict)

    example2 = SingleParent(name='parent2')

    assert isinstance(example2.to_json(), dict)


def test_schema_load(app):
    parent1 = SingleParent(name='parent1')

    assert SingleParent.save(parent1)

    schema1 = ParentSchema()
    parent2 = schema1.load(data=parent1.to_json(), unknown=EXCLUDE)

    assert parent1.active == parent2.active


def test_one_to_many(app):
    parent = SingleParent(name='parent1')
    child1 = Child(name="child1")
    child2 = Child(name="child2")

    assert SingleParent.save(parent)
    assert Child.save(child1)
    assert Child.save(child2)

    parent.children.append(child1)

    assert SingleParent.put(parent)
    assert child1.parent_id == parent.id
    assert parent.patch(parent.id, children=[child2])
    assert not (child1.parent_id == parent.id)
    assert child2.parent_id == parent.id

    child1.parent_id = parent.id

    assert Child.put(child1)
    assert child1 in parent.children
    assert Child.delete(child1.id)
    assert child1 not in parent.children
