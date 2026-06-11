# StudySpot – Study Places Management Platform

## Project Overview

StudySpot is a Flask-based web application that helps students discover and evaluate study locations.

The system supports three user roles:

- Student
- Owner
- Admin

Students can search and rate study places, owners can manage study locations, and administrators can approve places and manage users.

The application is connected to Azure SQL Database and includes authentication, authorization, ratings, messaging, and administrative approval workflows.
---

## Tech Stack

### Backend

- Python
- Flask
- SQLAlchemy
- Flask-Login
- Werkzeug Security

### Database

- Azure SQL Database
- SQLite (Testing Environment)

### Frontend

- HTML
- CSS
- JavaScript
- Jinja2 Templates

### Testing

- Pytest

### DevOps

- GitHub
- GitHub Actions
- Microsoft Azure
---

## Project Structure

```text
StudySpot/

app.py
models.py

templates/
    register.html
    login.html
    forgot_password.html
    view_map.html
    owner_dashboard.html
    admin_dashboard.html
    my_places.html
    add_place.html
    edit_place.html
    request_status.html
    view_ratings.html
    chat.html
    admin_requests.html
    admin_all_places.html
    admin_users.html

tests/
    conftest.py
    test_auth.py
    test_models.py
    test_4.py
    test_owner.py
    test_student_owner_features.py
    


static/

requirements.txt
README.md
```
---

## Database Models

### User

Stores:

- Username
- Email
- Password Hash
- Role (student / owner / admin)

### Place

Stores:

- Name
- Description
- Area
- Service Type
- Opening Hours
- WiFi
- Printer
- Latitude
- Longitude
- Status

### PlaceImage

Stores image URLs associated with study places.

### Message

Stores chat messages between Admin and Owner.

### Rating

Stores ratings and comments submitted by students.
---

## Main Routes

### Authentication

| Route | Purpose |
|---------|---------|
| /register | User registration |
| /login | User login |
| /forgot_password | Password reset |
| /logout | User logout |

### Student Routes

| Route | Purpose |
|---------|---------|
| /student_dashboard | Student dashboard |
| /view_map | View approved study places |
| /rate_place/<id> | Submit ratings |

### Owner Routes

| Route | Purpose |
|---------|---------|
| /owner_dashboard | Owner dashboard |
| /add_place | Add new place |
| /my_places | View owned places |
| /edit_place/<id> | Edit place |
| /delete_place/<id> | Delete place |
| /submit_request/<id> | Submit approval request |
| /request_status | View approval status |
| /view_ratings | View ratings |

### Admin Routes

| Route | Purpose |
|---------|---------|
| /admin_dashboard | Admin dashboard |
| /admin_requests | View pending requests |
| /approve_place/<id> | Approve place |
| /reject_place/<id> | Reject place |
| /return_place/<id> | Return place for editing |
| /admin_all_places | View all places |
| /admin_users | View all users |
| /delete_user/<id> | Delete user |

### Chat

| Route | Purpose |
|---------|---------|
| /chat/<place_id> | Messaging between Owner and Admin |
---

## Roles And Permissions

### Student

- View approved places
- Filter places by area
- Rate places
- View ratings

### Owner

- Add places
- Edit places
- Delete places
- Submit places for approval
- View ratings
- Chat with Admin

### Admin

- Approve places
- Reject places
- Return places for editing
- Manage users
- View all places
- Chat with Owners
---

## Security Features

- Password hashing using Werkzeug
- Flask-Login authentication
- Role-based authorization
- Protected routes using @login_required
- Password reset functionality
- Azure SQL integration
- SQL Injection prevention using SQLAlchemy ORM
---

## Testing

The project includes:

- Authentication Tests
- Authorization Tests
- Model Tests
- Admin Integration Tests

Run tests:

```bash
pytest
```
---

## Continuous Integration (CI)

The project uses GitHub Actions for Continuous Integration.

Current CI process:

1. Developer pushes code to GitHub.
2. GitHub Actions automatically runs tests.
3. The build is validated.
4. Developers verify that all tests pass before deployment.

Tools:

- GitHub Actions
- Pytest
---

## Azure Deployment

The application database is hosted on Microsoft Azure SQL Database.

Azure is used as the cloud platform for database management and project deployment.
---

## Implemented Features

- User Registration
- User Login
- Password Reset
- Role-Based Access Control
- Study Place Management
- Place Approval Workflow
- Student Ratings and Comments
- Admin–Owner Messaging System
- Azure SQL Database Integration
- Automated Testing with Pytest
---

## Team Members

- Salam Fregat
- Marwa diab 
- Shiamaa alnbary
- Maryem abu madigam
---

## Future Improvements

Future enhancements may include:

- Advanced search filters
- Real-time notifications
- Mobile-friendly improvements
- Analytics dashboard
- Enhanced recommendation system
---

## Conclusion

StudySpot provides a centralized platform for students to discover study locations, for owners to manage study places, and for administrators to control and approve content. The project demonstrates the use of Flask, SQLAlchemy, Azure SQL Database, authentication, authorization, testing, and cloud technologies in a real-world software engineering project.
## Templates And Pages

Implemented pages:

- register.html
- login.html
- forgot_password.html
- student_dashboard.html
- owner_dashboard.html
- admin_dashboard.html
- view_map.html
- add_place.html
- edit_place.html
- my_places.html
- request_status.html
- view_ratings.html
- admin_requests.html
- admin_all_places.html
- admin_users.html
- chat.html
## Data Storage

The primary persistence layer is Azure SQL Database.

Main tables used by the application:

- users
- place
- place_image
- message
- rating

The database is accessed through SQLAlchemy ORM.
## Run Locally

Install dependencies:

pip install -r requirements.txt

Run the application:

python app.py

Open:

http://127.0.0.1:5000
## Tests And CI

Run all tests:

pytest

The project uses GitHub Actions for Continuous Integration.

The CI pipeline automatically:

- Installs dependencies
- Runs automated tests
- Validates the build
## System Architecture

StudySpot follows a three-layer architecture:

1. Presentation Layer (HTML Templates)
   - User interface pages rendered using Jinja2 templates.

2. Application Layer (Flask Routes)
   - Handles authentication, authorization, business logic, and user actions.

3. Data Layer (Azure SQL Database)
   - Stores users, study places, ratings, messages, and images using SQLAlchemy ORM.

The communication flow is:

User → Flask Routes → SQLAlchemy → Azure SQL Database
## Database Relationships

The main relationships in the system are:

- One Owner can manage multiple study places.
- One Place can contain multiple images.
- One Place can receive multiple ratings.
- One Student can submit multiple ratings.
- Messages are exchanged between Admin and Owners regarding specific places.

These relationships are implemented using SQLAlchemy Foreign Keys and Relationships.
## Testing Strategy

Testing was performed using Pytest.

The project includes:

- Authentication tests
- Authorization tests
- Model tests
- Admin functionality tests
- Route access tests

The testing environment uses SQLite and isolated test data created through pytest fixtures.
## Cloud Integration

StudySpot uses Microsoft Azure as its cloud platform.

The project database is hosted on Azure SQL Database, allowing centralized storage and access to application data.

GitHub is used for version control and collaboration between team members.
## Security Design

Several security mechanisms were implemented:

- Password hashing using Werkzeug.
- Authentication with Flask-Login.
- Role-based access control.
- Protected routes using @login_required.
- Password reset functionality.
- SQL Injection protection through SQLAlchemy ORM.
## Development Process

The project was developed using Agile principles.

Development was managed through:

- Jira for sprint planning and task tracking.
- GitHub for source control.
- Feature branches for parallel development.
- Code reviews and pull requests.
- Continuous Integration using GitHub Actions.