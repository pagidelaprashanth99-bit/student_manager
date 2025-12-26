# Student Management System

A Flask-based web application for managing students, classes, and attendance.

## Setup Instructions

### 1. Install Dependencies

Make sure you have Python installed, then install the required packages:

```bash
pip install -r requirements.txt
```

### 2. Initialize Database

The database will be automatically created when you first run the application. However, if you need to reset it:

```bash
python reset_db.py
```

### 3. Create Teacher Account

Create a teacher account to login:

```bash
python create_teacher.py
```

**Default Teacher Credentials:**
- Username: `teacher`
- Password: `teacher123`

### 4. Run the Application

Start the Flask development server:

```bash
python run.py
```

The application will be available at: **http://127.0.0.1:5000**

### 5. Login

1. Open your web browser
2. Go to `http://127.0.0.1:5000`
3. Login with the teacher credentials:
   - Username: `teacher`
   - Password: `teacher123`

## Features

- **Teacher Dashboard:**
  - Add students
  - Create class schedules (with specific dates)
  - View all class schedules
  - Attendance analysis

- **Student Dashboard:**
  - View class schedules
  - Mark attendance during class time
  - View attendance records
  - See attendance percentage

## Troubleshooting

If you encounter database errors:
1. Stop the server (Ctrl+C)
2. Run: `python reset_db.py`
3. Run: `python create_teacher.py`
4. Restart: `python run.py`

## Notes

- The application uses SQLite database (`database.db`)
- Debug mode is enabled for development
- All passwords are hashed using Werkzeug

