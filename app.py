from flask import Flask, render_template
from flask_login import LoginManager
from models import db, User

app = Flask(__name__)

app.config['SECRET_KEY'] = 'my_secret_key_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///study_services.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login/student")
def login_student():
    return render_template("login_student.html")


@app.route("/login/owner")
def login_owner():
    return render_template("login_owner.html")


@app.route("/login/admin")
def login_admin():
    return render_template("login_admin.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)