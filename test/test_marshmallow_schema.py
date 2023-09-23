from uuid import uuid4
from datetime import datetime
from pytest import raises

from marshmallow import ValidationError

from test import app
from test.models.example import SingleParent
from test.models.example import ParentSchema
from test.models.example import Child
from test.models.example import ChildSchema
from test.models.example import SchoolClass
from test.models.example import SchoolClassSchema
from test.models.example import BaseModel
from test.models.example import BaseSchema


def test_dump_dict(app):
    parent1 = SingleParent(name='parent1')
    schema = ParentSchema()

    assert isinstance(schema.dump(parent1), dict)


def test_dump_field_keys(app):
    parent1 = SingleParent(name='parent1')
    child1 = Child(name='child1')
    parent1.children.append(child1)
    SingleParent.post(parent1)
    schema = ParentSchema()
    parent_dict = schema.dump(parent1)

    assert 'id' in parent_dict.keys()
    assert 'created' in parent_dict.keys()
    assert 'updated' in parent_dict.keys()
    assert 'active' in parent_dict.keys()
    assert 'name' in parent_dict.keys()
    assert 'children' in parent_dict.keys()

    child_schema = ChildSchema()
    school_class1 = SchoolClass(name='class1')
    school_class1.attendees.append(child1)
    SchoolClass.post(school_class1)
    child_dict = child_schema.dump(child1)

    assert 'id' in child_dict.keys()
    assert 'created' in child_dict.keys()
    assert 'updated' in child_dict.keys()
    assert 'active' in child_dict.keys()
    assert 'name' in child_dict.keys()
    assert 'parent' in child_dict.keys()
    assert 'classes' in child_dict.keys()

    school_class_schema = SchoolClassSchema()
    school_class_dict = school_class_schema.dump(school_class1)

    assert 'id' in school_class_dict.keys()
    assert 'created' in school_class_dict.keys()
    assert 'updated' in school_class_dict.keys()
    assert 'active' in school_class_dict.keys()
    assert 'name' in school_class_dict.keys()
    assert 'attendees' in school_class_dict.keys()


def test_load_class_and_fields():
    parent1 = SingleParent(name='parent1')
    parent1.id = uuid4()
    parent1.active = True
    time1 = datetime.now()
    parent1.created = time1
    parent1.updated = time1
    schema = ParentSchema()
    loaded_parent = schema.load(parent1.to_json())

    assert isinstance(loaded_parent, SingleParent)
    assert loaded_parent.id == parent1.id
    assert loaded_parent.active == parent1.active
    assert loaded_parent.created == parent1.created
    assert loaded_parent.updated == parent1.updated
    assert loaded_parent.name == parent1.name


def test_load_validation_error_handling():
    parent1 = SingleParent(name='parent1')
    parent1.id = uuid4()
    parent1.active = True
    time1 = datetime.now()
    parent1.created = time1
    parent1.updated = 12
    schema = ParentSchema()
    with raises(ValidationError):
        schema.load(parent1.to_json())
