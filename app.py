
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import urllib.parse
from models import db, User, Place, PlaceImage, Message, Rating

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'

password = "StudySpot@2026Team13"

connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=studyspot-team13-sql.database.windows.net;"
    "DATABASE=studyspotdb;"
    "UID=studyspotadmin;"
    f"PWD={password};"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
    "Connection Timeout=60;"
)

params = urllib.parse.quote_plus(connection_string)

app.config['SQLALCHEMY_DATABASE_URI'] = f"mssql+pyodbc:///?odbc_connect={params}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
                return redirect(url_for('view_map'))

            if user.role == 'owner':
                return redirect(url_for('owner_dashboard'))

            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))

        flash('Invalid email or password.')

    return render_template('login.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        user = User.query.filter_by(email=email).first()

        if not user:
            flash('No account found with this email.', 'danger')
            return redirect(url_for('forgot_password'))

        if new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('forgot_password'))

        if len(new_password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return redirect(url_for('forgot_password'))

        user.password_hash = generate_password_hash(new_password)
        db.session.commit()

        flash('Password updated successfully. Please sign in.', 'success')
        return redirect(url_for('login'))

    return render_template('forgot_password.html')


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


@app.route('/rate_place/<int:place_id>', methods=['POST'])
@login_required
def rate_place(place_id):
    if current_user.role != 'student':
        flash('Only students can rate places.')
        return redirect(url_for('home'))

    place = Place.query.get_or_404(place_id)

    score = int(request.form['score'])
    comment = request.form['comment']

    existing_rating = Rating.query.filter_by(
        student_id=current_user.id,
        place_id=place.id
    ).first()

    if existing_rating:
        existing_rating.score = score
        existing_rating.comment = comment
    else:
        new_rating = Rating(
            student_id=current_user.id,
            place_id=place.id,
            score=score,
            comment=comment
        )
        db.session.add(new_rating)

    db.session.commit()

    return redirect(url_for('view_map'))


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
            status='pending'
        )

        db.session.add(new_place)
        db.session.commit()

        image_url = request.form.get('image_url')

        if image_url and image_url.strip():
            place_image = PlaceImage(
                filename=image_url.strip(),
                place_id=new_place.id
            )
            db.session.add(place_image)

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

        image_url = request.form.get('image_url')
        if image_url and image_url.strip():
            if place.images:
                place.images[0].filename = image_url.strip()
            else:
                place_image = PlaceImage(
                    filename=image_url.strip(),
                    place_id=place.id
                )
                db.session.add(place_image)

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


@app.route('/view_ratings')
@login_required
def view_ratings():
    if current_user.role != 'owner':
        flash('Unauthorized access.')
        return redirect(url_for('home'))

    places = Place.query.filter_by(owner_id=current_user.id).all()

    return render_template('view_ratings.html', places=places)


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


@app.route('/admin_all_places')
@login_required
def admin_all_places():
    if current_user.role != 'admin':
        flash('Unauthorized access.')
        return redirect(url_for('home'))

    places = Place.query.all()
    return render_template('admin_all_places.html', places=places)


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


@app.route('/chat/<int:place_id>', methods=['GET', 'POST'])
@login_required
def chat(place_id):
    place = Place.query.get_or_404(place_id)

    if current_user.role == 'owner':
        if place.owner_id != current_user.id:
            flash('Unauthorized access.')
            return redirect(url_for('owner_dashboard'))

        admin = User.query.filter_by(role='admin').first()

        if not admin:
            flash('Admin user does not exist.')
            return redirect(url_for('owner_dashboard'))

        receiver_id = admin.id

    elif current_user.role == 'admin':
        receiver_id = place.owner_id

    else:
        flash('Unauthorized access.')
        return redirect(url_for('home'))

    if request.method == 'POST':
        content = request.form['content']

        if content.strip():
            new_message = Message(
                sender_id=current_user.id,
                receiver_id=receiver_id,
                place_id=place.id,
                content=content
            )

            db.session.add(new_message)
            db.session.commit()

        return redirect(url_for('chat', place_id=place.id))

    messages = Message.query.filter(
        Message.place_id == place.id,
        (
            ((Message.sender_id == current_user.id) & (Message.receiver_id == receiver_id)) |
            ((Message.sender_id == receiver_id) & (Message.receiver_id == current_user.id))
        )
    ).order_by(Message.timestamp.asc()).all()

    return render_template(
        'chat.html',
        place=place,
        messages=messages
    )


@app.route('/admin_users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash('Unauthorized access.')
        return redirect(url_for('home'))

    users = User.query.all()

    return render_template('admin_users.html', users=users)


@app.route('/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Unauthorized access.')
        return redirect(url_for('home'))

    user = User.query.get_or_404(user_id)

    if user.role == 'admin':
        return redirect(url_for('admin_users'))

    if user.role == 'owner':
        places = Place.query.filter_by(owner_id=user.id).all()

        for place in places:
            db.session.delete(place)

    db.session.delete(user)
    db.session.commit()

    return redirect(url_for('admin_users'))


# =========================
# Logout
# =========================
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('register'))


if __name__ == '__main__':
    app.run(debug=True)