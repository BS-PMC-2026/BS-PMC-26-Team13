import pytest
from app import app


@pytest.fixture
def client():
    # Creates a Flask test client.
    # Used to simulate requests without opening the browser.
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client


# Checks that an unauthenticated user cannot view My Places.
# Expected result: redirect to login page (302).
def test_my_places_requires_login(client):
    response = client.get('/my_places')
    assert response.status_code == 302


# Checks that an unauthenticated user cannot edit a place.
# Expected result: redirect to login page (302).
def test_edit_place_requires_login(client):
    response = client.get('/edit_place/1')
    assert response.status_code == 302


# Checks that an unauthenticated user cannot delete a place.
# Expected result: redirect to login page (302).
def test_delete_place_requires_login(client):
    response = client.get('/delete_place/1')
    assert response.status_code == 302


# Checks that an unauthenticated user cannot submit a place request.
# Expected result: redirect to login page (302).
def test_submit_request_requires_login(client):
    response = client.get('/submit_request/1')
    assert response.status_code == 302


# Checks that an unauthenticated user cannot access Request Status.
# Expected result: redirect to login page (302).
def test_request_status_requires_login(client):
    response = client.get('/request_status')
    assert response.status_code == 302


# Checks that an unauthenticated user cannot view Ratings.
# Expected result: redirect to login page (302).
def test_view_ratings_requires_login(client):
    response = client.get('/view_ratings')
    assert response.status_code == 302