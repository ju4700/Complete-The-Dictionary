# Complete-The-Dictionary
It is a practice Flask application "Complete the Dictionary" which is designed to gamify the process of expanding a dictionary. Users can register, log in, and contribute words to earn points based on the uniqueness of each word they submit. This was to see the difference between django and Flask. A little side project to learn about Flask and a bit of SQL (At the time of the project).

## Key Features:
* User Registration and Authentication:
  New users can register with a unique username and password.
  Passwords are securely hashed using the pbkdf2:sha256 hashing method for storage in the database.
  Existing users can log in to their accounts securely.
* User Roles:
  Users have roles (user by default), but administrators (admin) have additional privileges.
  Administrators can manage users (view, delete) and words submitted by users.
* Word Submission:
  Users can submit up to 50 unique words per day.
  Submitted words are checked against a set of valid words (VALID_WORDS) to ensure they are acceptable.
  Each unique word submitted by a user earns them points.
* Leaderboard:
  Displays top users based on the number of unique words they have contributed.
  Users are ranked by their score (number of unique words submitted).
* Notifications:
  Users receive notifications for actions such as successfully adding a word, encountering an invalid word, or reaching the daily limit of word submissions.
  Notifications can be viewed and marked as read by the user.
* Admin Panel:
  Administrators have access to an admin dashboard where they can view all users and words.
  They can delete users and words if necessary.

![Screenshot from 2024-06-21 21-01-30](https://github.com/ju4700/Complete-The-Dictionary/assets/137766031/ad7d4ba9-961e-48ff-b702-4f92e0e94d23)

### Data Persistence:
Data such as users, words, and notifications are stored in a SQLite database (dictionary_game.db) using SQLAlchemy ORM.

### Technology Stack:
  * Backend: Flask (Python web framework)
  * Database: SQLite (for local development, can be scaled to other SQL databases for production)
  * ORM: SQLAlchemy (object-relational mapping)
  * Frontend: HTML templates rendered with Jinja2, styled with CSS
  * Authentication: Flask-Login for managing user sessions
  * Form Handling: Flask-WTF for form validation and rendering
