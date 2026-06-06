from app import app, db
from models import User, Place, PlaceImage, Message, Rating
from werkzeug.security import generate_password_hash


# Test for model: User
def test_create_user_model(client):
    with app.app_context():
        user = User(
            username="TestUser",
            email="testuser@gmail.com",
            password_hash=generate_password_hash("123456"),
            role="student"
        )

        db.session.add(user)
        db.session.commit()

        saved_user = User.query.filter_by(email="testuser@gmail.com").first()

        assert saved_user is not None
        assert saved_user.username == "TestUser"
        assert saved_user.role == "student"


# Test for model: Place
def test_create_place_model(client):
    with app.app_context():
        owner = User.query.filter_by(role="owner").first()

        place = Place(
            name="Model Test Place",
            description="Testing place model",
            area="Beersheba",
            service_type="Library",
            opening_hours="08:00 - 18:00",
            wifi=True,
            printer=False,
            latitude=31.25,
            longitude=34.79,
            owner_id=owner.id,
            status="pending"
        )

        db.session.add(place)
        db.session.commit()

        saved_place = Place.query.filter_by(name="Model Test Place").first()

        assert saved_place is not None
        assert saved_place.description == "Testing place model"
        assert saved_place.owner_id == owner.id
        assert saved_place.status == "pending"


# Test for model: PlaceImage
def test_create_place_image_model(client):
    with app.app_context():
        place = Place.query.first()

        image = PlaceImage(
            filename="https://example.com/image.jpg",
            place_id=place.id
        )

        db.session.add(image)
        db.session.commit()

        saved_image = PlaceImage.query.filter_by(place_id=place.id).first()

        assert saved_image is not None
        assert saved_image.filename == "https://example.com/image.jpg"


# Test for model: Message
def test_create_message_model(client):
    with app.app_context():
        admin = User.query.filter_by(role="admin").first()
        owner = User.query.filter_by(role="owner").first()
        place = Place.query.first()

        message = Message(
            sender_id=admin.id,
            receiver_id=owner.id,
            place_id=place.id,
            content="Hello from model test"
        )

        db.session.add(message)
        db.session.commit()

        saved_message = Message.query.filter_by(content="Hello from model test").first()

        assert saved_message is not None
        assert saved_message.sender_id == admin.id
        assert saved_message.receiver_id == owner.id
        assert saved_message.place_id == place.id


# Test for model: Rating
def test_create_rating_model(client):
    with app.app_context():
        student = User.query.filter_by(role="student").first()
        place = Place.query.first()

        rating = Rating(
            student_id=student.id,
            place_id=place.id,
            score=5,
            comment="Great place"
        )

        db.session.add(rating)
        db.session.commit()

        saved_rating = Rating.query.filter_by(
            student_id=student.id,
            place_id=place.id
        ).first()

        assert saved_rating is not None
        assert saved_rating.score == 5
        assert saved_rating.comment == "Great place"