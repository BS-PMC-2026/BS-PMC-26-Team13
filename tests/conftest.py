import os
import pytest
from werkzeug.security import generate_password_hash

os.environ["TESTING"] = "1"

from app import app, db
from models import User, Place


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.app_context():
        db.drop_all()
        db.create_all()

        admin = User(
            username="Admin",
            email="admin@gmail.com",
            password_hash=generate_password_hash("1234"),
            role="admin"
        )

        owner = User(
            username="Owner",
            email="owner@gmail.com",
            password_hash=generate_password_hash("1234"),
            role="owner"
        )

        student = User(
            username="Student",
            email="student@gmail.com",
            password_hash=generate_password_hash("1234"),
            role="student"
        )

        db.session.add_all([admin, owner, student])
        db.session.commit()

        place = Place(
            name="Test Place",
            description="Test description",
            area="Beersheba",
            service_type="Library",
            opening_hours="08:00 - 18:00",
            wifi=True,
            printer=True,
            latitude=31.25,
            longitude=34.79,
            owner_id=owner.id,
            status="pending"
        )

        db.session.add(place)
        db.session.commit()

    with app.test_client() as client:
        yield client


def login(client, email, password="1234"):
    return client.post(
        "/login",
        data={
            "email": email,
            "password": password
        },
        follow_redirects=False
    )