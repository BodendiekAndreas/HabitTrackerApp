from datetime import timedelta, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db


# Database model for a user. Inherits from flask_login's UserMixin and SQLAlchemy's Model.
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    habits = db.relationship('Habit', backref='user', lazy='dynamic')

    def __init__(self, username: str, email: str):
        self.username = username
        self.email = email

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return '<User ' + self.username + '>'


# Database model for user habits. Each habit has a name,
# description, periodicity and is related to the user.
class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(128))
    periodicity = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    completed = db.Column(db. Boolean, default=False)
    streak = db.Column(db.Integer, default=0)
    completions = db.relationship('Completion', backref='habit', lazy='dynamic')
    reminders = db.relationship('Reminder', backref='habit', lazy='dynamic')
    created_at = db.Column(db.DateTime, default=db.func.now())
    completed_count = db.Column(db.Integer, nullable=True, default=0)

    @property
    def is_in_current_period(self):
        if self.last_completed is None:
            return False
        elif self.periodicity == 'daily':
            return self.last_completed == date.today()
        elif self.periodicity == 'weekly':
            days_since_created = (date.today() - self.created_at.date()).days
            days_since_completed = (date.today() - self.last_completed).days

            return days_since_created // 7 == days_since_completed // 7
        else:
            raise ValueError('Invalid periodicity: ' + self.periodicity)

    @property
    def is_broken(self):
        if self.last_completed is None:
            return False
        elif self.periodicity == 'daily':
            return self.last_completed < date.today() - timedelta(days=1)
        elif self.periodicity == 'weekly':
            return self.last_completed < date.today() - timedelta(weeks=1)
        else:
            raise ValueError('Invalid periodicity: ' + self.periodicity)

    def __repr__(self):
        return '<Habit ' + self.name + '>'


# Database model for habit completion.
# Each completion has a timestamp and is related to a habit.
class Completion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    completed_at = db.Column(db.DateTime, default=db.func.now())
    habit_id = db.Column(db.Integer, db.ForeignKey('habit.id'))
    count = db.Column(db.Integer, default=1)  # Add this line

    @property
    def completed_date(self):
        return self.completed_at.date()

    def __repr__(self):
        return '<Completion ' + str(self.id) + '>'


# Database model for habit reminders.
# Each reminder has a message, date and is related to a habit.
class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255))
    date = db.Column(db.Date)
    habit_id = db.Column(db.Integer, db.ForeignKey('habit.id'))

    def __repr__(self):
        return '<Reminder ' + self.message + '>'
