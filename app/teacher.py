from flask import Blueprint, render_template, request, redirect, flash
from flask_login import login_required
from app import db
from app.models import Student, User, Attendance, ClassSchedule
from werkzeug.security import generate_password_hash
from datetime import datetime, date

teacher_bp = Blueprint("teacher", __name__, url_prefix="/teacher")

@teacher_bp.route("/")
@login_required
def dashboard():
    try:
        schedules = ClassSchedule.query.all()
    except Exception as e:
        flash(f"Database error: {str(e)}. Please restart the application.", "error")
        schedules = []
    return render_template("teacher/dashboard.html", schedules=schedules)

@teacher_bp.route("/add-student", methods=["GET", "POST"])
@login_required
def add_student():
    if request.method == "POST":
        try:
            username = request.form["username"]
            password = request.form["password"]
            name = request.form["name"]
            
            # Check if username already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash("Username already exists. Please choose a different username.", "error")
                return render_template("teacher/add_student.html")
            
            if not username or not password or not name:
                flash("All fields are required.", "error")
                return render_template("teacher/add_student.html")

            hashed_password = generate_password_hash(password)
            user = User(username=username, password=hashed_password, role="student")
            db.session.add(user)
            db.session.commit()

            student = Student(name=name, user_id=user.id)
            db.session.add(student)
            db.session.commit()

            flash(f"Student '{name}' added successfully!", "success")
            
            # Check if user wants to add another
            if request.form.get("add_another"):
                return render_template("teacher/add_student.html")
            else:
                return redirect("/teacher")
        except Exception as e:
            flash(f"Error adding student: {str(e)}", "error")
            return render_template("teacher/add_student.html")

    return render_template("teacher/add_student.html")


@teacher_bp.route("/create-class", methods=["GET", "POST"])
@login_required
def create_class():
    if request.method == "POST":
        try:
            class_name = request.form["class_name"]
            class_date_str = request.form["class_date"]
            start_time_str = request.form["start_time"]
            end_time_str = request.form["end_time"]
            
            if not class_name or not class_date_str or not start_time_str or not end_time_str:
                flash("All fields are required.", "error")
                return render_template("teacher/create_class.html")
            
            # Parse date and time strings
            class_date = datetime.strptime(class_date_str, "%Y-%m-%d").date()
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
            end_time = datetime.strptime(end_time_str, "%H:%M").time()
            
            # Validate that end time is after start time
            if end_time <= start_time:
                flash("End time must be after start time.", "error")
                return render_template("teacher/create_class.html")
            
            schedule = ClassSchedule(
                class_name=class_name,
                class_date=class_date,
                start_time=start_time,
                end_time=end_time
            )
            db.session.add(schedule)
            db.session.commit()
            flash(f"Class '{class_name}' scheduled successfully!", "success")
            
            # Check if user wants to add another
            if request.form.get("add_another"):
                return render_template("teacher/create_class.html")
            else:
                return redirect("/teacher")
        except ValueError as e:
            flash(f"Invalid date or time format. Please check your input.", "error")
            return render_template("teacher/create_class.html")
        except Exception as e:
            flash(f"Error creating class: {str(e)}", "error")
            return render_template("teacher/create_class.html")
    
    return render_template("teacher/create_class.html")

@teacher_bp.route("/delete-class/<int:class_id>")
@login_required
def delete_class(class_id):
    schedule = ClassSchedule.query.get_or_404(class_id)
    db.session.delete(schedule)
    db.session.commit()
    flash("Class schedule deleted successfully!", "success")
    return redirect("/teacher")

@teacher_bp.route("/students")
@login_required
def list_students():
    students = Student.query.all()
    # Get user info for each student
    students_with_user = []
    for student in students:
        user = User.query.get(student.user_id)
        students_with_user.append({
            'student': student,
            'username': user.username if user else 'N/A'
        })
    return render_template("teacher/students.html", students=students_with_user)

@teacher_bp.route("/delete-student/<int:student_id>")
@login_required
def delete_student(student_id):
    try:
        student = Student.query.get_or_404(student_id)
        user_id = student.user_id
        student_name = student.name
        
        # Delete all attendance records for this student
        Attendance.query.filter_by(student_id=student.id).delete()
        
        # Delete the student record
        db.session.delete(student)
        
        # Delete the associated user account
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
        
        db.session.commit()
        flash(f"Student '{student_name}' and all associated data deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting student: {str(e)}", "error")
    
    return redirect("/teacher/students")

@teacher_bp.route("/analysis")
@login_required
def analysis():
    students = Student.query.all()
    total_classes = ClassSchedule.query.count()
    report = []

    for s in students:
        present = Attendance.query.filter(
            Attendance.student_id == s.id,
            Attendance.status == True,
            Attendance.class_schedule_id.isnot(None)
        ).count()
        percent = (present / total_classes) * 100 if total_classes else 0
        report.append((s.name, percent))

    return render_template("teacher/analysis.html", report=report)
