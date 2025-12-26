"""
Database migration script to update ClassSchedule table
from day_of_week to class_date
"""
from app import create_app, db
from app.models import ClassSchedule, Attendance, Student, User
import sqlite3
import os

app = create_app()

with app.app_context():
    # Check if database exists
    db_path = os.path.join(os.path.dirname(__file__), "database.db")
    
    if os.path.exists(db_path):
        print("Database exists. Checking schema...")
        
        # Connect to database to check columns
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("PRAGMA table_info(class_schedule)")
        columns = [row[1] for row in cursor.fetchall()]
        
        has_day_of_week = 'day_of_week' in columns
        has_class_date = 'class_date' in columns
        
        conn.close()
        
        if has_day_of_week and not has_class_date:
            print("Old schema detected. Dropping and recreating tables...")
            # Drop all tables
            db.drop_all()
            # Recreate with new schema
            db.create_all()
            print("Database schema updated successfully!")
        elif has_class_date:
            print("Database already has the correct schema.")
        else:
            print("Creating new database with correct schema...")
            db.create_all()
            print("Database created successfully!")
    else:
        print("Database does not exist. Creating new database...")
        db.create_all()
        print("Database created successfully!")

print("\nMigration complete! You can now run the application.")

