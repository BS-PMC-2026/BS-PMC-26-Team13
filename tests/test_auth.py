from models import User
from app import db, load_user
from werkzeug.security import check_password_hash


# Tests that load_user returns the correct user when a valid ID exists.
from app import app


# Tests that load_user returns the correct user when a valid ID exists.
def test_load_user_existing():
    with app.app_context():
        user = load_user(1)

        assert user is not None
        assert user.email == "admin@gmail.com"


# Tests that load_user returns None when the user ID does not exist.
def test_load_user_not_existing():
    with app.app_context():
        user = load_user(999)

        assert user is None


# Tests that the home route redirects users to the registration page.
def test_home_redirect(client):
    response = client.get("/")

    assert response.status_code == 302
    assert "/register" in response.location


# Tests that the register page is accessible via a GET request.
def test_register_get(client):
    response = client.get("/register")

    assert response.status_code == 200


# Tests successful registration of a new student account.
def test_register_student_success(client):
    response = client.post(
        "/register",
        data={
            "username": "New Student",
            "email": "newstudent@gmail.com",
            "password": "123456",
            "role": "student"
        },
        follow_redirects=False
    )

    assert response.status_code == 302
    assert "/login" in response.location

    user = User.query.filter_by(email="newstudent@gmail.com").first()

    assert user is not None
    assert user.role == "student"


# Tests successful registration of a new owner account.
def test_register_owner_success(client):
    response = client.post(
        "/register",
        data={
            "username": "New Owner",
            "email": "newowner@gmail.com",
            "password": "123456",
            "role": "owner"
        },
        follow_redirects=False
    )

    assert response.status_code == 302
    assert "/login" in response.location

    user = User.query.filter_by(email="newowner@gmail.com").first()

    assert user is not None
    assert user.role == "owner"


# Tests that registration fails when the email is already registered.
def test_register_duplicate_email(client):
    response = client.post(
        "/register",
        data={
            "username": "Someone",
            "email": "student@gmail.com",
            "password": "123456",
            "role": "student"
        },
        follow_redirects=False
    )

    assert response.status_code == 302
    assert "/register" in response.location


# Tests that registration fails when an invalid role is provided.
def test_register_invalid_role(client):
    response = client.post(
        "/register",
        data={
            "username": "Bad User",
            "email": "bad@gmail.com",
            "password": "123456",
            "role": "admin"
        },
        follow_redirects=False
    )

    assert response.status_code == 302
    assert "/register" in response.location


# Tests successful login and redirection for a student user.
def test_login_student_success(client):
    response = client.post(
        "/login",
        data={
            "email": "student@gmail.com",
            "password": "1234"
        },
        follow_redirects=False
    )

    assert response.status_code == 302
    assert "/view_map" in response.location


# Tests successful login and redirection for an owner user.
def test_login_owner_success(client):
    response = client.post(
        "/login",
        data={
            "email": "owner@gmail.com",
            "password": "1234"
        },
        follow_redirects=False
    )

    assert response.status_code == 302
    assert "/owner_dashboard" in response.location


# Tests successful login and redirection for an admin user.
def test_login_admin_success(client):
    response = client.post(
        "/login",
        data={
            "email": "admin@gmail.com",
            "password": "1234"
        },
        follow_redirects=False
    )

    assert response.status_code == 302
    assert "/admin_dashboard" in response.location


# Tests that login fails when an incorrect password is entered.
def test_login_wrong_password(client):
    response = client.post(
        "/login",
        data={
            "email": "student@gmail.com",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 200


# Tests that login fails when the email does not exist in the system.
def test_login_unknown_email(client):
    response = client.post(
        "/login",
        data={
            "email": "unknown@gmail.com",
            "password": "1234"
        }
    )

    assert response.status_code == 200


# Tests that password reset fails when the email is not found.
def test_forgot_password_email_not_found(client):
    response = client.post(
        "/forgot_password",
        data={
            "email": "none@gmail.com",
            "new_password": "123456",
            "confirm_password": "123456"
        },
        follow_redirects=False
    )

    assert response.status_code == 302
    assert "/forgot_password" in response.location


# Tests that password reset fails when the passwords do not match.
def test_forgot_password_mismatch(client):
    response = client.post(
        "/forgot_password",
        data={
            "email": "student@gmail.com",
            "new_password": "123456",
            "confirm_password": "654321"
        },
        follow_redirects=False
    )

    assert response.status_code == 302
    assert "/forgot_password" in response.location


# Tests that password reset fails when the new password is shorter than six characters.
def test_forgot_password_short_password(client):
    response = client.post(
        "/forgot_password",
        data={
            "email": "student@gmail.com",
            "new_password": "123",
            "confirm_password": "123"
        },
        follow_redirects=False
    )

    assert response.status_code == 302
    assert "/forgot_password" in response.location


# Tests successful password reset and verifies the password is updated in the database.
def test_forgot_password_success(client):
    response = client.post(
        "/forgot_password",
        data={
            "email": "student@gmail.com",
            "new_password": "newpassword",
            "confirm_password": "newpassword"
        },
        follow_redirects=False
    )

    assert response.status_code == 302
    assert "/login" in response.location

    user = User.query.filter_by(email="student@gmail.com").first()

    assert check_password_hash(user.password_hash, "newpassword")


# Tests that create_admin does not create a duplicate admin account when one already exists.
def test_create_admin_when_exists(client):
    response = client.get("/create_admin")

    assert response.status_code == 302
    assert "/login" in response.location