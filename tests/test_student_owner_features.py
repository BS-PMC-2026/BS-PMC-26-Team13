import uuid

import pytest
from werkzeug.security import generate_password_hash

from app import app, db
from models import User, Place, PlaceImage, Rating


TEST_PREFIX = "pytest_marwa_"


@pytest.fixture(autouse=True)
def app_context():
    with app.app_context():
        yield


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def unique_text(name):
    return f"{TEST_PREFIX}{name}_{uuid.uuid4().hex[:8]}"


def create_user(role):
    email = unique_text(role) + "@test.com"

    user = User(
        username=unique_text(role),
        email=email,
        password_hash=generate_password_hash("123456"),
        role=role
    )

    db.session.add(user)
    db.session.commit()

    return user


def create_place(owner, status="approved"):
    place = Place(
        name=unique_text("place"),
        description="Test place description",
        area="Test Area",
        service_type="Cafe",
        opening_hours="08:00-22:00",
        wifi=True,
        printer=True,
        latitude=31.2518,
        longitude=34.7913,
        owner_id=owner.id,
        status=status
    )

    db.session.add(place)
    db.session.commit()

    return place


def login_as(client, user):
    with client.session_transaction() as session:
        session["_user_id"] = str(user.id)
        session["_fresh"] = True


def cleanup_test_data():
    test_places = Place.query.filter(Place.name.like(f"{TEST_PREFIX}%")).all()

    for place in test_places:
        PlaceImage.query.filter_by(place_id=place.id).delete(synchronize_session=False)
        Rating.query.filter_by(place_id=place.id).delete(synchronize_session=False)
        db.session.delete(place)

    Rating.query.filter(Rating.comment.like(f"{TEST_PREFIX}%")).delete(synchronize_session=False)
    User.query.filter(User.email.like(f"{TEST_PREFIX}%")).delete(synchronize_session=False)

    db.session.commit()


@pytest.fixture(autouse=True)
def clean_database():
    cleanup_test_data()
    yield
    cleanup_test_data()


def test_student_dashboard_rejects_non_student(client):
    owner = create_user("owner")
    login_as(client, owner)

    response = client.get("/student_dashboard", follow_redirects=False)

    assert response.status_code == 302
    assert response.location.endswith("/")


def test_view_map_loads_for_student_and_shows_approved_place(client):
    student = create_user("student")
    owner = create_user("owner")
    place = create_place(owner, status="approved")

    login_as(client, student)

    response = client.get("/view_map")

    assert response.status_code == 200
    assert place.name.encode() in response.data


def test_rate_place_creates_rating_for_student(client):
    student = create_user("student")
    owner = create_user("owner")
    place = create_place(owner, status="approved")

    login_as(client, student)

    response = client.post(
        f"/rate_place/{place.id}",
        data={
            "score": "5",
            "comment": TEST_PREFIX + "great place"
        },
        follow_redirects=False
    )

    rating = Rating.query.filter_by(
        student_id=student.id,
        place_id=place.id
    ).first()

    assert response.status_code == 302
    assert rating is not None
    assert rating.score == 5
    assert rating.comment == TEST_PREFIX + "great place"


def test_owner_dashboard_loads_for_owner(client):
    owner = create_user("owner")
    login_as(client, owner)

    response = client.get("/owner_dashboard")

    assert response.status_code == 200


def test_add_place_get_loads_for_owner(client):
    owner = create_user("owner")
    login_as(client, owner)

    response = client.get("/add_place")

    assert response.status_code == 200


def test_add_place_post_creates_pending_place_and_image(client):
    owner = create_user("owner")
    login_as(client, owner)

    place_name = unique_text("added_place")
    image_url = "https://example.com/test-image.jpg"

    response = client.post(
        "/add_place",
        data={
            "name": place_name,
            "description": "Created by pytest",
            "area": "Test Area",
            "service_type": "Library",
            "opening_hours": "09:00-18:00",
            "latitude": "31.2518",
            "longitude": "34.7913",
            "wifi": "on",
            "printer": "on",
            "image_url": image_url
        },
        follow_redirects=False
    )

    place = Place.query.filter_by(name=place_name).first()

    assert response.status_code == 302
    assert place is not None
    assert place.status == "pending"
    assert place.owner_id == owner.id
    assert place.wifi is True
    assert place.printer is True

    image = PlaceImage.query.filter_by(place_id=place.id).first()

    assert image is not None
    assert image.filename == image_url