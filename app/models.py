from app import db, login_manager
from flask_login import UserMixin
from datetime import date, datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")

def india_now():
    return datetime.now(IST).replace(tzinfo=None)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(10))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    user = db.relationship("User", backref="student_profile")

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=india_now)

class StudentSubject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"))
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"))
    created_at = db.Column(db.DateTime, default=india_now)

class ClassSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_date = db.Column(db.Date, default=date.today)

class ClassSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(100))
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=True)
    class_date = db.Column(db.Date)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    created_at = db.Column(db.DateTime, default=india_now)

class StudentClassAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"))
    class_schedule_id = db.Column(db.Integer, db.ForeignKey("class_schedule.id"))
    created_at = db.Column(db.DateTime, default=india_now)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer)
    class_id = db.Column(db.Integer)
    class_schedule_id = db.Column(db.Integer, db.ForeignKey("class_schedule.id"))
    status = db.Column(db.Boolean)
    marked_at = db.Column(db.DateTime, default=india_now)
    medical_report_path = db.Column(db.String(300), nullable=True)
    updated_by_emergency = db.Column(db.Boolean, default=False)

class AttendancePercentageOverride(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"))
    subject_name = db.Column(db.String(100))
    percentage = db.Column(db.Float)
    updated_at = db.Column(db.DateTime, default=india_now)
