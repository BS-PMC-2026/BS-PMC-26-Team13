from app import db
from models import User, Place, Message
from tests.conftest import login


# Test for function: admin_dashboard
def test_admin_dashboard_access(client):
    login(client, "admin@gmail.com")

    response = client.get("/admin_dashboard")

    assert response.status_code == 200


# Test for function: admin_requests
def test_admin_requests_access(client):
    login(client, "admin@gmail.com")

    response = client.get("/admin_requests")

    assert response.status_code == 200


# Test for function: admin_all_places
def test_admin_all_places_access(client):
    login(client, "admin@gmail.com")

    response = client.get("/admin_all_places")

    assert response.status_code == 200


# Test for function: approve_place
def test_approve_place(client):
    login(client, "admin@gmail.com")

    place = Place.query.first()

    response = client.get(f"/approve_place/{place.id}", follow_redirects=False)

    updated_place = Place.query.get(place.id)

    assert response.status_code == 302
    assert updated_place.status == "approved"


# Test for function: reject_place
def test_reject_place(client):
    login(client, "admin@gmail.com")

    place = Place.query.first()

    response = client.get(f"/reject_place/{place.id}", follow_redirects=False)

    updated_place = Place.query.get(place.id)

    assert response.status_code == 302
    assert updated_place.status == "rejected"


# Test for function: return_place
def test_return_place(client):
    login(client, "admin@gmail.com")

    place = Place.query.first()

    response = client.get(f"/return_place/{place.id}", follow_redirects=False)

    updated_place = Place.query.get(place.id)

    assert response.status_code == 302
    assert updated_place.status == "returned_for_edit"


# Test for function: chat
def test_admin_chat_page_access(client):
    login(client, "admin@gmail.com")

    place = Place.query.first()

    response = client.get(f"/chat/{place.id}")

    assert response.status_code == 200


# Test for function: chat
def test_admin_send_chat_message(client):
    login(client, "admin@gmail.com")

    place = Place.query.first()

    response = client.post(
        f"/chat/{place.id}",
        data={"content": "Test message from admin"},
        follow_redirects=False
    )

    message = Message.query.filter_by(content="Test message from admin").first()

    assert response.status_code == 302
    assert message is not None
    assert message.place_id == place.id


# Test for function: admin_users
def test_admin_users_access(client):
    login(client, "admin@gmail.com")

    response = client.get("/admin_users")

    assert response.status_code == 200


# Test for function: delete_user
def test_delete_user(client):
    login(client, "admin@gmail.com")

    owner = User.query.filter_by(role="owner").first()

    response = client.get(f"/delete_user/{owner.id}", follow_redirects=False)

    deleted_user = User.query.get(owner.id)

    assert response.status_code == 302
    assert deleted_user is None


# Test for function: logout
def test_logout(client):
    login(client, "admin@gmail.com")

    response = client.get("/logout", follow_redirects=False)

    assert response.status_code == 302
    assert "/register" in response.location