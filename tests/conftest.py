import pytest
import os
import logging
from app import create_app, db

os.environ['TESTING'] = 'True'
class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-key'

@pytest.fixture
def app():
    app = create_app(TestConfig)
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db_setup(app):
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

# run using: python3 -m pytest
# see which p/f: python3 -m pytest -v
# specific file: python3 -m pytest tests/test_auth.py