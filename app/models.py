from app import db, login_manager
from flask_login import UserMixin
from datetime import date, datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(10))  # teacher / student

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    user_id = db.Column(db.Integer)

class ClassSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_date = db.Column(db.Date, default=date.today)

class ClassSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(100))
    class_date = db.Column(db.Date)  # Specific date for the class
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now())

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer)
    class_id = db.Column(db.Integer)  # For backward compatibility with ClassSession
    class_schedule_id = db.Column(db.Integer, db.ForeignKey('class_schedule.id'))  # Link to ClassSchedule
    status = db.Column(db.Boolean)  # True = Present
    marked_at = db.Column(db.DateTime, default=lambda: datetime.now())
