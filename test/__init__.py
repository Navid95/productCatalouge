import pytest

from app import create_app, Test
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
