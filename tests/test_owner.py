import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client


def test_owner_dashboard_requires_login(client):
    response = client.get('/owner_dashboard')
    assert response.status_code == 302


def test_my_places_requires_login(client):
    response = client.get('/my_places')
    assert response.status_code == 302


def test_request_status_requires_login(client):
    response = client.get('/request_status')
    assert response.status_code == 302


def test_view_ratings_requires_login(client):
    response = client.get('/view_ratings')
    assert response.status_code == 302