import uuid

from test.models.example import SingleParent
from test.models.example import Child
from test.models.example import SchoolClass
from test import app


def test_model_save(app):
    parent = SingleParent(name='parent1')

    assert SingleParent.post(parent)
    assert parent.id
    assert not SingleParent.post(parent)
    assert not SingleParent.post(list([1, 2, 3]))


def test_model_get(app):
    parent1 = SingleParent(name='parent1')

    assert SingleParent.post(parent1)

    parent2 = SingleParent.get(parent1.id)

    assert parent1 == parent2


def test_model_patch(app):
    parent1 = SingleParent(name='parent1')

    assert SingleParent.post(parent1)

    updated_time1 = parent1.updated

    assert SingleParent.patch(parent1.id, name='parent1 edited')
    assert updated_time1 != parent1.updated

    parent1.blah = 'wow'

    assert SingleParent.patch(parent1.id, blah='blah')

    parent2 = SingleParent.get(parent1.id)

    assert hasattr(parent2, 'blah')


def test_model_put(app):
    parent1 = SingleParent(name='parent1')

    assert SingleParent.post(parent1)

    sample_text = f'test_model_put'
    parent1.name = sample_text

    assert SingleParent.put(parent1)

    parent2 = SingleParent.get(parent1.id)

    assert parent2
    assert parent1.updated == parent2.updated
    assert parent2.name == sample_text


def test_model_delete(app):
    parent1 = SingleParent(name='parent1')

    assert SingleParent.post(parent1)

    id1 = parent1.id

    assert SingleParent.delete(id1)
    assert not SingleParent.get(id1)
    assert not SingleParent.delete(uuid.uuid4())


def test_model_to_json(app):
    parent1 = SingleParent(name='parent1')

    assert SingleParent.post(parent1)
    assert isinstance(parent1.to_json(), dict)

    example2 = SingleParent(name='parent2')

    assert isinstance(example2.to_json(), dict)


def test_one_to_many(app):
    parent = SingleParent(name='parent1')
    child1 = Child(name="child1")
    child2 = Child(name="child2")

    assert SingleParent.post(parent)
    assert Child.post(child1)
    assert Child.post(child2)

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

    child3 = Child(name='child3')
    child3.parent = parent

    assert Child.post(child3)
    assert child3 in parent.children


def test_many_to_many(app):
    school_class1 = SchoolClass(name='class1')
    child1 = Child(name='child1')

    assert SchoolClass.post(school_class1)
    assert Child.post(child1)

    school_class1.attendees.append(child1)

    assert SchoolClass.put(school_class1)

    school_class2 = SchoolClass.get(school_class1.id)

    assert school_class2
    assert child1 in school_class2.attendees
    assert Child.delete(child1.id)
    assert child1 not in school_class2.attendees

    child2 = Child(name='child2')
    child2.classes.append(school_class2)

    assert Child.post(child2)
    assert child2 in school_class2.attendees
    assert SchoolClass.delete(school_class2.id)
    assert school_class2 not in child2.classes
