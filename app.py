""" from flask import Flask, render_template
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

@app.route("/register/student")
def register_student():
    return render_template("register_student.html")

@app.route("/login/owner")
def login_owner():
    return render_template("login_owner.html")


@app.route("/register/owner")
def register_owner():
    return render_template("register_owner.html")

@app.route("/login/admin")
def login_admin():
    return render_template("login_admin.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True) """

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Place

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///study_services.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_student'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()


@app.route('/create_admin')
def create_admin():
    existing_admin = User.query.filter_by(email='admin@gmail.com').first()

    if existing_admin:
        flash('Admin already exists.')
        return redirect(url_for('login_admin'))

    admin = User(
        username='Admin',
        email='admin@gmail.com',
        password_hash=generate_password_hash('1234'),
        role='admin'
    )

    db.session.add(admin)
    db.session.commit()

    flash('Admin created successfully. You can now log in.')
    return redirect(url_for('login_admin'))


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register_student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('This email is already registered.')
            return redirect(url_for('register_student'))

        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role='student'
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Student registered successfully.')
        return redirect(url_for('login_student'))

    return render_template('register_student.html')


@app.route('/register_owner', methods=['GET', 'POST'])
def register_owner():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('This email is already registered.')
            return redirect(url_for('register_owner'))

        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role='owner'
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Owner registered successfully.')
        return redirect(url_for('login_owner'))

    return render_template('register_owner.html')


@app.route('/login_student', methods=['GET', 'POST'])
def login_student():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email, role='student').first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Student login successful.')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid student email or password.')

    return render_template('login_student.html')

@app.route('/student_dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        flash('Unauthorized access.')
        return redirect(url_for('home'))

    return render_template('student_dashboard.html')

@app.route('/view_map')
@login_required
def view_map():
    if current_user.role != 'student':
        flash('Unauthorized access.')
        return redirect(url_for('home'))

    places = Place.query.filter_by(status='approved').all()
    return render_template('view_map.html', places=places)


@app.route('/login_owner', methods=['GET', 'POST'])
def login_owner():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email, role='owner').first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Owner login successful.')
            return redirect(url_for('owner_dashboard'))
        else:
            flash('Invalid owner email or password.')

    return render_template('login_owner.html')


@app.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email, role='admin').first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Admin login successful.')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin email or password.')

    return render_template('login_admin.html')

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Unauthorized access.')
        return redirect(url_for('home'))

    return render_template('admin_dashboard.html')

@app.route('/add_place', methods=['GET', 'POST'])
@login_required
def add_place():
    if current_user.role != 'owner':
        flash('Only owners can add places.')
        return redirect(url_for('home'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        area = request.form['area']
        service_type = request.form['service_type']
        opening_hours = request.form['opening_hours']
        latitude = request.form['latitude']
        longitude = request.form['longitude']

        wifi = True if request.form.get('wifi') == 'on' else False
        printer = True if request.form.get('printer') == 'on' else False

        new_place = Place(
            name=name,
            description=description,
            area=area,
            service_type=service_type,
            opening_hours=opening_hours,
            wifi=wifi,
            printer=printer,
            latitude=float(latitude),
            longitude=float(longitude),
            owner_id=current_user.id
        )

        db.session.add(new_place)
        db.session.commit()

        flash('Place added successfully and sent for approval.')
        return redirect(url_for('owner_dashboard'))

    return render_template('add_place.html')


@app.route('/owner_dashboard')
@login_required
def owner_dashboard():
    if current_user.role != 'owner':
        flash('Unauthorized access.')
        return redirect(url_for('home'))

    return render_template('owner_dashboard.html')

@app.route('/my_places')
@login_required
def my_places():
    if current_user.role != 'owner':
        flash('Unauthorized access.')
        return redirect(url_for('owner_dashboard'))

    places = Place.query.filter_by(owner_id=current_user.id).all()
    return render_template('my_places.html', places=places)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('home'))



if __name__ == '__main__':
    app.run(debug=True)