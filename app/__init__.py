from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import os
import sqlite3

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from app.auth import auth_bp
    from app.teacher import teacher_bp
    from app.student import student_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)

    with app.app_context():
        # Check if database needs migration
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database.db")
        
        try:
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Check if class_schedule table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='class_schedule'")
                table_exists = cursor.fetchone() is not None
                
                if table_exists:
                    cursor.execute("PRAGMA table_info(class_schedule)")
                    columns = [row[1] for row in cursor.fetchall()]
                    
                    has_day_of_week = 'day_of_week' in columns
                    has_class_date = 'class_date' in columns
                    
                    # If old schema exists, drop and recreate
                    if has_day_of_week and not has_class_date:
                        print("Migrating database schema from day_of_week to class_date...")
                        conn.close()
                        db.drop_all()
                        db.create_all()
                        print("Database migration complete!")
                    elif not has_class_date:
                        # Table exists but missing class_date column
                        print("Updating database schema...")
                        conn.close()
                        db.drop_all()
                        db.create_all()
                        print("Database schema updated!")
                    else:
                        conn.close()
                        # Schema is correct, just ensure all tables exist
                        db.create_all()
                else:
                    conn.close()
                    # Table doesn't exist, create it
                    db.create_all()
            else:
                # Database doesn't exist, create it
                db.create_all()
        except Exception as e:
            # If there's any error, recreate the database
            print(f"Error checking database: {e}")
            print("Recreating database...")
            try:
                db.drop_all()
            except:
                pass
            db.create_all()
            print("Database recreated successfully!")
        
        # Auto-create teacher account if it doesn't exist
        from app.models import User
        from werkzeug.security import generate_password_hash
        teacher = User.query.filter_by(role="teacher").first()
        if not teacher:
            print("Creating default teacher account...")
            default_teacher = User(
                username="teacher",
                password=generate_password_hash("teacher123"),
                role="teacher"
            )
            db.session.add(default_teacher)
            db.session.commit()
            print("Default teacher account created!")
            print("Username: teacher")
            print("Password: teacher123")
            print("⚠️  Please change the password after first login!")
    
    return app
