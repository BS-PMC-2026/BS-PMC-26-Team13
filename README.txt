StudySpot

Team 13

Project Description:
StudySpot is a web application designed to help students find suitable study places in Be'er Sheva. The system includes three user roles:

1. Student

   * View approved study places on a map.
   * Search and filter places.
   * View ratings and reviews.
   * Submit ratings and comments.

2. Owner

   * Add study places.
   * Edit or delete places.
   * Submit places for approval.
   * View ratings and communicate with the administrator.

3. Administrator

   * Approve, reject, or return places for editing.
   * Manage users.
   * Communicate with place owners.

Technologies Used:

* Python
* Flask
* SQLAlchemy
* Azure SQL Database
* HTML / CSS / JavaScript
* Leaflet Maps
* GitHub
* Pytest

Installation:

1. Clone the https://github.com/BS-PMC-2026/BS-PMC-26-Team13.git.

2. Create and activate a virtual environment.

3. Install dependencies:

   pip install -r requirements.txt

4. Run the application:

   python app.py

Testing:
Run all tests using:

python -m pytest tests -v

Repository Structure:

* app.py
* models.py
* templates/
* static/
* tests/
* requirements.txt