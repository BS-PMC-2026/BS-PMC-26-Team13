from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # student / owner / admin

    places = db.relationship('Place', backref='owner', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"


class Place(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    area = db.Column(db.String(100), nullable=False)
    service_type = db.Column(db.String(100), nullable=False)
    opening_hours = db.Column(db.String(100), nullable=True)
    wifi = db.Column(db.Boolean, default=False)
    printer = db.Column(db.Boolean, default=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), default="pending")
    

    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    images = db.relationship('PlaceImage', backref='place', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Place {self.name}>"


class PlaceImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(500), nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'), nullable=False)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'), nullable=False)

    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')
    place = db.relationship('Place', backref='messages')

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'), nullable=False)

    score = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    student = db.relationship('User', backref='ratings')
    place = db.relationship('Place', backref='ratings')




    