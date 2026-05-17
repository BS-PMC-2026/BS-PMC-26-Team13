from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
from models import db, User, Place, PlaceImage

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///study_services.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()


@app.route('/create_admin')
def create_admin():
    existing_admin = User.query.filter_by(email='admin@gmail.com').first()

    if existing_admin:
        return redirect(url_for('login'))

    admin = User(
        username='Admin',
        email='admin@gmail.com',
        password_hash=generate_password_hash('1234'),
        role='admin'
    )

    db.session.add(admin)
    db.session.commit()

    return redirect(url_for('login'))


@app.route('/')
def home():
    return redirect(url_for('register'))

# =========================
# Unified Register
# =========================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        if role not in ['student', 'owner']:
            flash('Please select a valid role.')
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('This email is already registered.')
            return redirect(url_for('register'))

        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=role
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')


# =========================
# Unified Login
# =========================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)

            if user.role == 'student':
                return redirect(url_for('student_dashboard'))

            if user.role == 'owner':
                return redirect(url_for('owner_dashboard'))

            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))

        flash('Invalid email or password.')

    return render_template('login.html')


# =========================
# Student Pages
# =========================
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

    selected_area = request.args.get('area')

    all_areas = db.session.query(Place.area).filter_by(status='approved').distinct().all()
    areas = [area[0] for area in all_areas]

    query = Place.query.filter_by(status='approved')

    if selected_area and selected_area != 'all':
        query = query.filter_by(area=selected_area)

    places = query.all()

    places_data = []
    for place in places:
        places_data.append({
            'name': place.name,
            'description': place.description or 'No description',
            'area': place.area,
            'service_type': place.service_type,
            'opening_hours': place.opening_hours or 'Not specified',
            'wifi': 'Yes' if place.wifi else 'No',
            'printer': 'Yes' if place.printer else 'No',
            'latitude': place.latitude,
            'longitude': place.longitude
        })

    return render_template(
        'view_map.html',
        places=places,
        places_data=places_data,
        areas=areas,
        selected_area=selected_area
    )


# =========================
# Owner Pages
# =========================
@app.route('/owner_dashboard')
@login_required
def owner_dashboard():
    if current_user.role != 'owner':
        flash('Unauthorized access.')
        return redirect(url_for('home'))

    return render_template('owner_dashboard.html')


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

        image_filename = None
        image = request.files.get('image')

        if image and image.filename != '':
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

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
            owner_id=current_user.id,
            status='pending',
            image_filename=image_filename
        )

        db.session.add(new_place)
        db.session.commit()

        return redirect(url_for('owner_dashboard'))

    return render_template('add_place.html')

@app.route('/my_places')
@login_required
def my_places():
    if current_user.role != 'owner':
        flash('Unauthorized access.')
        return redirect(url_for('home'))

    places = Place.query.filter_by(owner_id=current_user.id).all()
    return render_template('my_places.html', places=places)



@app.route('/edit_place/<int:place_id>', methods=['GET', 'POST'])
@login_required
def edit_place(place_id):
    if current_user.role != 'owner':
        flash('Unauthorized access.')
        return redirect(url_for('home'))

    place = Place.query.get_or_404(place_id)

    if place.owner_id != current_user.id:
        flash('You can edit only your own places.')
        return redirect(url_for('my_places'))

    if request.method == 'POST':
        place.name = request.form['name']
        place.description = request.form['description']
        place.area = request.form['area']
        place.service_type = request.form['service_type']
        place.opening_hours = request.form['opening_hours']
        place.latitude = float(request.form['latitude'])
        place.longitude = float(request.form['longitude'])
        place.wifi = True if request.form.get('wifi') == 'on' else False
        place.printer = True if request.form.get('printer') == 'on' else False
        place.status = 'pending'

        db.session.commit()
        return redirect(url_for('my_places'))

    return render_template('edit_place.html', place=place)


@app.route('/delete_place/<int:place_id>')
@login_required
def delete_place(place_id):
    if current_user.role != 'owner':
        flash('Unauthorized access.')
        return redirect(url_for('home'))

    place = Place.query.get_or_404(place_id)

    if place.owner_id != current_user.id:
        flash('You can delete only your own places.')
        return redirect(url_for('my_places'))

    db.session.delete(place)
    db.session.commit()

    return redirect(url_for('my_places'))


@app.route('/submit_request/<int:place_id>')
@login_required
def submit_request(place_id):
    if current_user.role != 'owner':
        flash('Unauthorized access.')
        return redirect(url_for('home'))

    place = Place.query.get_or_404(place_id)

    if place.owner_id != current_user.id:
        flash('Unauthorized access.')
        return redirect(url_for('my_places'))

    place.status = 'pending'
    db.session.commit()

    return redirect(url_for('request_status'))


@app.route('/request_status')
@login_required
def request_status():
    if current_user.role != 'owner':
        flash('Unauthorized access.')
        return redirect(url_for('home'))

    places = Place.query.filter_by(owner_id=current_user.id).all()
    return render_template('request_status.html', places=places)


# =========================
# Admin Pages
# =========================
@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Unauthorized access.')
        return redirect(url_for('home'))

    return render_template('admin_dashboard.html')


@app.route('/admin_requests')
@login_required
def admin_requests():
    if current_user.role != 'admin':
        flash('Unauthorized access.')
        return redirect(url_for('home'))

    pending_places = Place.query.filter_by(status='pending').all()
    return render_template('admin_requests.html', places=pending_places)


@app.route('/approve_place/<int:place_id>')
@login_required
def approve_place(place_id):
    if current_user.role != 'admin':
        flash('Unauthorized access.')
        return redirect(url_for('home'))

    place = Place.query.get_or_404(place_id)
    place.status = 'approved'
    db.session.commit()

    return redirect(url_for('admin_requests'))


@app.route('/reject_place/<int:place_id>')
@login_required
def reject_place(place_id):
    if current_user.role != 'admin':
        flash('Unauthorized access.')
        return redirect(url_for('home'))

    place = Place.query.get_or_404(place_id)
    place.status = 'rejected'
    db.session.commit()

    return redirect(url_for('admin_requests'))


@app.route('/return_place/<int:place_id>')
@login_required
def return_place(place_id):
    if current_user.role != 'admin':
        flash('Unauthorized access.')
        return redirect(url_for('home'))

    place = Place.query.get_or_404(place_id)
    place.status = 'returned_for_edit'
    db.session.commit()

    return redirect(url_for('admin_requests'))


# =========================
# Logout
# =========================
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)