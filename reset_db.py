"""
Script to reset the database with the new schema
This will delete all existing data and recreate tables
"""
from app import create_app, db
from app.models import User, Student, ClassSchedule, Attendance

app = create_app()

with app.app_context():
    print("Dropping all tables...")
    db.drop_all()
    print("Creating new tables with updated schema...")
    db.create_all()
    print("\nDatabase reset complete!")
    print("Note: All existing data has been deleted.")
    print("You may need to recreate your teacher account using create_teacher.py")

