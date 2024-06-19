from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dictionary_game.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), default='user')
    words = db.relationship('Word', backref='author', lazy=True)

class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template('register.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/")
def home():
    return render_template('home.html')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/admin")
@login_required
@admin_required
def admin():
    users = User.query.all()
    words = Word.query.all()
    return render_template('admin.html', users=users, words=words)

@app.route("/admin/delete_user/<int:user_id>")
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User has been deleted!', 'success')
    return redirect(url_for('admin'))

@app.route("/admin/delete_word/<int:word_id>")
@login_required
@admin_required
def delete_word(word_id):
    word = Word.query.get_or_404(word_id)
    db.session.delete(word)
    db.session.commit()
    flash('Word has been deleted!', 'success')
    return redirect(url_for('admin'))

@app.route("/leaderboard")
def leaderboard():
    users = User.query.all()
    leaderboard_data = []

    for user in users:
        unique_words = {word.word for word in user.words}
        leaderboard_data.append({'username': user.username, 'score': len(unique_words)})

    leaderboard_data = sorted(leaderboard_data, key=lambda x: x['score'], reverse=True)
    return render_template('leaderboard.html', leaderboard=leaderboard_data)

VALID_WORDS = {'apple', 'banana', 'cherry'}  # A comprehensive set or use an API

def notify_user(user, message):
    notification = Notification(message=message, user_id=user.id)
    db.session.add(notification)
    db.session.commit()

@app.route("/submit_word", methods=['GET', 'POST'])
@login_required
def submit_word():
    if request.method == 'POST':
        word = request.form.get('word').lower()
        if word not in VALID_WORDS:
            notify_user(current_user, f"Word '{word}' is invalid!")
            flash('Invalid word!', 'danger')
            return render_template('submit_word.html')

        start_of_day = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        user_words_today = Word.query.filter(
            Word.author == current_user,
            Word.timestamp >= start_of_day,
            Word.timestamp < end_of_day
        ).count()

        if user_words_today < 50:
            existing_word = Word.query.filter_by(word=word).first()
            if not existing_word:
                new_word = Word(word=word, author=current_user)
                db.session.add(new_word)
                db.session.commit()
                notify_user(current_user, f"Word '{word}' added successfully!")
                flash('Word added successfully!', 'success')
            else:
                notify_user(current_user, f"Word '{word}' already exists!")
                flash('Word already exists!', 'danger')
        else:
            notify_user(current_user, "You have reached the daily limit of 50 words!")
            flash('You have reached the daily limit of 50 words!', 'danger')
    return render_template('submit_word.html')

@app.route("/notifications")
@login_required
def notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id, read=False).all()
    for notification in notifications:
        notification.read = True
    db.session.commit()
    return render_template('notifications.html', notifications=notifications)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
