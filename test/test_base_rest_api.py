from test import app
from test import client
from test.models.example import SingleParent
from test.models.example import SingleParentSchema


def test_get_api(client):
    parent1 = SingleParent(name='parent1')
    SingleParent.post(parent1)
    response = client.get(f'/parents/{parent1.id.__str__()}')
    assert response.status_code == 200
    response = client.get(f'/parents/1')
    assert response.status_code == 404

