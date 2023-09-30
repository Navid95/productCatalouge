from test import app
from test import client
from test.models.example import SingleParent
from test.models.example import SingleParentSchema
from test.models.example import Child


def test_get_api(client):
    parent1 = SingleParent(name='parent1')
    SingleParent.post(parent1)
    response = client.get(f'/parents/{parent1.id.__str__()}')
    assert response.status_code == 200
    response = client.get(f'/parents/1')
    assert response.status_code == 404


def test_post_api(client):
    parent1 = SingleParent(name='parent1')
    parent_schema = SingleParentSchema(only=('name', 'children'))
    response = client.post(f'/parents', json=parent_schema.dump(parent1))
    assert response.status_code == 200
    assert 'parent' in response.json.keys()


def test_put_api(client):
    parent1 = SingleParent(name='parent1')
    parent_schema = SingleParentSchema(only=('name', 'children'))
    response = client.post(f'/parents', json=parent_schema.dump(parent1))

    assert response.status_code == 200
    assert 'parent' in response.json.keys()
    assert response.json['parent']

    parent1 = SingleParentSchema().load({'parent': response.json['parent']})
    parent_schema2 = SingleParentSchema(exclude=('created', 'updated', 'children'))
    json_data = parent_schema2.dump(parent1)
    json_data['parent']['name'] = 'updated name for parent 1'
    response2 = client.put(f'/parents', json=json_data)

    assert response2.status_code == 200
    assert 'parent' in response2.json.keys()
    assert response2.json['parent']
    assert response2.json['parent']['name'] == json_data['parent']['name']


def test_get_all(client):
    parent1 = SingleParent(name='parent1')
    parent2 = SingleParent(name='parent2')
    parent3 = SingleParent(name='parent3')
    parent_schema = SingleParentSchema(only=('name', 'children'))

    assert client.post(f'/parents', json=parent_schema.dump(parent1)).status_code == 200
    assert client.post(f'/parents', json=parent_schema.dump(parent2)).status_code == 200
    assert client.post(f'/parents', json=parent_schema.dump(parent3)).status_code == 200

    response = client.get(f'/parents', query_string={'page': '1'})

    assert response.status_code == 200
    assert len(response.json['parents']) == 3


def test_delete(client):
    parent1 = SingleParent(name='parent1')
    parent2 = SingleParent(name='parent2')
    parent3 = SingleParent(name='parent3')
    parent_schema = SingleParentSchema(only=('name', 'children'))
    load_schema = SingleParentSchema()
    parent1 = load_schema.load(client.post(f'/parents', json=parent_schema.dump(parent1)).json)
    parent2 = load_schema.load(client.post(f'/parents', json=parent_schema.dump(parent2)).json)
    parent3 = load_schema.load(client.post(f'/parents', json=parent_schema.dump(parent3)).json)

    response = client.delete(f'/parents/{parent1.id}')

    assert response.status_code == 200
    assert response.json['response'] == True

    assert client.get(f'/parents/{parent1.id.__str__()}').json.get('parent', {}) == {}
