from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from werkzeug.security import generate_password_hash
from datetime import datetime

from app import db
from app.models import (
    User,
    Student,
    ClassSchedule,
    StudentClassAssignment,
    Attendance,
    AttendancePercentageOverride,
)

teacher_bp = Blueprint("teacher", __name__, url_prefix="/teacher")


@teacher_bp.route("/")
@login_required
def teacher_home():
    return redirect(url_for("teacher.dashboard"))


@teacher_bp.route("/dashboard")
@login_required
def dashboard():
    classes = ClassSchedule.query.order_by(ClassSchedule.class_date.desc()).all()
    return render_template("teacher/dashboard.html", classes=classes)


@teacher_bp.route("/students")
@login_required
def students():
    students = Student.query.all()
    return render_template("teacher/students.html", students=students)


@teacher_bp.route("/students/add", methods=["GET", "POST"])
@login_required
def add_student():
    if request.method == "POST":
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")

        user = User(
            username=username,
            password=generate_password_hash(password),
            role="student"
        )
        db.session.add(user)
        db.session.commit()

        student = Student(name=name, user_id=user.id)
        db.session.add(student)
        db.session.commit()

        return redirect(url_for("teacher.students"))

    return render_template("teacher/add_student.html")


@teacher_bp.route("/students/edit/<int:student_id>", methods=["GET", "POST"])
@login_required
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)
    user = User.query.get(student.user_id)

    if request.method == "POST":
        student.name = request.form.get("name")
        user.username = request.form.get("username")

        new_password = request.form.get("password")
        if new_password:
            user.password = generate_password_hash(new_password)

        db.session.commit()
        return redirect(url_for("teacher.students"))

    return render_template("teacher/edit_student.html", student=student, user=user)


@teacher_bp.route("/students/delete/<int:student_id>")
@login_required
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    user = User.query.get(student.user_id)

    Attendance.query.filter_by(student_id=student.id).delete()
    StudentClassAssignment.query.filter_by(student_id=student.id).delete()
    AttendancePercentageOverride.query.filter_by(student_id=student.id).delete()

    db.session.delete(student)

    if user:
        db.session.delete(user)

    db.session.commit()
    return redirect(url_for("teacher.students"))


@teacher_bp.route("/create_class", methods=["GET", "POST"])
@login_required
def create_class():
    students = Student.query.all()

    if request.method == "POST":
        class_name = request.form.get("class_name")
        class_date = datetime.strptime(request.form.get("class_date"), "%Y-%m-%d").date()
        start_time = datetime.strptime(request.form.get("start_time"), "%H:%M").time()
        end_time = datetime.strptime(request.form.get("end_time"), "%H:%M").time()
        selected_students = request.form.getlist("students")

        new_class = ClassSchedule(
            class_name=class_name,
            class_date=class_date,
            start_time=start_time,
            end_time=end_time,
        )
        db.session.add(new_class)
        db.session.commit()

        for student_id in selected_students:
            assignment = StudentClassAssignment(
                student_id=int(student_id),
                class_schedule_id=new_class.id
            )
            db.session.add(assignment)

        db.session.commit()
        return redirect(url_for("teacher.dashboard"))

    return render_template("teacher/create_class.html", students=students)


@teacher_bp.route("/take_attendance/<int:class_id>", methods=["GET", "POST"])
@login_required
def take_attendance(class_id):
    class_schedule = ClassSchedule.query.get_or_404(class_id)

    assignments = StudentClassAssignment.query.filter_by(
        class_schedule_id=class_id
    ).all()

    students = []
    for assignment in assignments:
        student = Student.query.get(assignment.student_id)
        if student:
            students.append(student)

    if request.method == "POST":
        for student in students:
            status_value = request.form.get(f"status_{student.id}")
            is_present = status_value == "present"

            attendance = Attendance.query.filter_by(
                student_id=student.id,
                class_schedule_id=class_id
            ).first()

            if attendance:
                attendance.status = is_present
            else:
                attendance = Attendance(
                    student_id=student.id,
                    class_id=class_id,
                    class_schedule_id=class_id,
                    status=is_present
                )
                db.session.add(attendance)

        db.session.commit()
        return redirect(url_for("teacher.dashboard"))

    records = Attendance.query.filter_by(class_schedule_id=class_id).all()
    attendance_map = {record.student_id: record.status for record in records}

    return render_template(
        "teacher/take_attendance.html",
        class_schedule=class_schedule,
        students=students,
        attendance_map=attendance_map
    )


@teacher_bp.route("/analysis", methods=["GET", "POST"])
@login_required
def analysis():
    if request.method == "POST":
        student_id = int(request.form.get("student_id"))
        subject_name = request.form.get("subject_name")
        percentage = float(request.form.get("percentage"))

        override = AttendancePercentageOverride.query.filter_by(
            student_id=student_id,
            subject_name=subject_name
        ).first()

        if override:
            override.percentage = percentage
        else:
            override = AttendancePercentageOverride(
                student_id=student_id,
                subject_name=subject_name,
                percentage=percentage
            )
            db.session.add(override)

        db.session.commit()
        return redirect(url_for("teacher.analysis"))

    result = []

    for student in Student.query.all():
        assignments = StudentClassAssignment.query.filter_by(
            student_id=student.id
        ).all()

        subjects = {}

        for assignment in assignments:
            class_schedule = ClassSchedule.query.get(assignment.class_schedule_id)

            if not class_schedule:
                continue

            subject = class_schedule.class_name

            if subject not in subjects:
                subjects[subject] = {
                    "student": student,
                    "subject": subject,
                    "attended": 0,
                    "total": 0,
                    "percentage": 0
                }

            subjects[subject]["total"] += 1

            attendance = Attendance.query.filter_by(
                student_id=student.id,
                class_schedule_id=class_schedule.id,
                status=True
            ).first()

            if attendance:
                subjects[subject]["attended"] += 1

        for subject_name, data in subjects.items():
            if data["total"] > 0:
                data["percentage"] = round(
                    (data["attended"] / data["total"]) * 100,
                    2
                )

            override = AttendancePercentageOverride.query.filter_by(
                student_id=student.id,
                subject_name=subject_name
            ).first()

            if override:
                data["percentage"] = override.percentage

            result.append(data)

    return render_template("teacher/analysis.html", result=result)
