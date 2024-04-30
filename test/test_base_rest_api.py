from test import app
from test import client
from test.models.example import SingleParent
from test.models.example import SingleParentSchema
from test.models.example import Child


def test_get_api(client):
    with client:
        parent1 = SingleParent(name='parent1')
        SingleParent.post(parent1)
        response = client.get(f'/parents/{str(parent1.id)}')

        assert response.status_code == 200

        response = client.get(f'/parents/1')

        assert response.status_code == 404

        parent1.children.append(Child(name='child1'))
        SingleParent.put(parent1)

        response = client.get(f'parents/{str(parent1.id)}/children')
        assert parent1.children
        assert response.status_code == 200
        assert response.json['children']

        response = client.get(f'/parents/{str(parent1.id)}')

        assert response.status_code == 200


def test_post_api(client):
    with client:
        parent1 = SingleParent(name='parent1')
        parent_schema = SingleParentSchema(only=['name'])
        response = client.post(f'/parents', json=parent_schema.dump(parent1))
        assert response.status_code == 200
        assert 'parent' in response.json.keys()


def test_put_api(client):
    with client:
        parent1 = SingleParent(name='parent1')
        parent_schema = SingleParentSchema(only=['name'])
        response = client.post(f'/parents', json=parent_schema.dump(parent1))

        assert response.status_code == 200
        assert 'parent' in response.json.keys()
        assert response.json['parent']

        json_data = {'parent': response.json['parent']}
        parent1 = SingleParentSchema().load(json_data)
        parent_schema2 = SingleParentSchema(exclude=('created', 'updated'))
        json_data = parent_schema2.dump(parent1)
        json_data['parent']['name'] = 'updated name for parent 1'
        response2 = client.put(f'/parents', json=json_data)

        assert response2.status_code == 200
        assert 'parent' in response2.json.keys()
        assert response2.json['parent']
        assert response2.json['parent']['name'] == json_data['parent']['name']


def test_get_all(client):
    with client:
        parent1 = SingleParent(name='parent1')
        parent2 = SingleParent(name='parent2')
        parent3 = SingleParent(name='parent3')
        parent_schema = SingleParentSchema(only=['name'])

        assert client.post(f'/parents', json=parent_schema.dump(parent1)).status_code == 200
        assert client.post(f'/parents', json=parent_schema.dump(parent2)).status_code == 200
        assert client.post(f'/parents', json=parent_schema.dump(parent3)).status_code == 200

        response = client.get(f'/parents', query_string={'page': '1'})

        assert response.status_code == 200
        assert len(response.json['parents']) == 3


def test_delete(client):
    with client:
        parent1 = SingleParent(name='parent1')
        parent2 = SingleParent(name='parent2')
        parent3 = SingleParent(name='parent3')
        parent_schema = SingleParentSchema(only=['name'])
        load_schema = SingleParentSchema()

        parent1_response = client.post(f'/parents', json=parent_schema.dump(parent1)).json
        parent2_response = client.post(f'/parents', json=parent_schema.dump(parent2)).json
        parent3_response = client.post(f'/parents', json=parent_schema.dump(parent3)).json

        parent1 = load_schema.load(parent1_response)
        parent2 = load_schema.load(parent2_response)
        parent3 = load_schema.load(parent3_response)

        response = client.delete(f'/parents/{parent1.id}')

        assert response.status_code == 200
        assert response.json['result'] == True

        assert client.get(f'/parents/{str(parent1.id)}').json.get('parent', {}) == {}


def test_get_relationship(client):
    with client:
        parent1 = SingleParent(name='parent1')
        parent1.children.append(Child(name='child1'))
        parent1.children.append(Child(name='child2'))
        SingleParent.post(parent1)
        response = client.get(f'/parents/{str(parent1.id)}/children')

        assert response.status_code == 200
        assert len(response.json['children']) == 2


def test_put_relationship(client):
    with client:
        parent1 = SingleParent(name='parent1')
        SingleParent.post(parent1)
        child1 = Child(name='child1')
        child2 = Child(name='child2')
        child3 = Child(name='child3')
        Child.post(child1)
        Child.post(child2)
        Child.post(child3)

        response = client.put(f'/parents/{str(parent1.id)}/children', json={'children': [{'id': str(child1.id)}]})

        assert response.status_code == 200
        assert len(response.json['children']) == 1
        for child in response.json['children']:
            assert child.get('parent_id', None) == str(parent1.id)

        json_data = {'children': [{'id': str(child2.id)}, {'id': str(child3.id)}]}
        response = client.put(f'/parents/{str(parent1.id)}/children', json=json_data)

        assert response.status_code == 200
        assert len(response.json['children']) == 2

        for child in response.json['children']:
            assert child.get('parent_id', None) == str(parent1.id)
            assert child.get('id', None) != str(child1.id)


def test_get_relationship_by_id(client):
    with client:
        parent1 = SingleParent(name='parent1')
        child1 = Child(name='child1')
        child2 = Child(name='child2')
        child3 = Child(name='child3')
        children = [child1, child2]
        parent1.children = children
        SingleParent.post(parent1)

        response = client.get(f'/parents/{str(parent1.id)}/children/{str(child1.id)}')

        assert response.status_code == 200
        assert response.json['child']['id'] == str(child1.id)

        response = client.get(f'/parents/{str(parent1.id)}/children/{str(child3.id)}')

        assert response.status_code == 404


def test_delete_relationship_by_id(client):
    with client:
        parent1 = SingleParent(name='parent1')
        child1 = Child(name='child1')
        child2 = Child(name='child2')
        child3 = Child(name='child3')
        children = [child1, child2]
        parent1.children = children
        SingleParent.post(parent1)

        response = client.delete(f'/parents/{str(parent1.id)}/children/{str(child1.id)}')

        assert response.status_code == 200
        assert response.json['response']

        response = client.delete(f'/parents/{str(parent1.id)}/children/{str(child3.id)}')

        assert response.status_code == 404
        assert not response.json
