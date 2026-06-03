from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import (
    Student,
    Subject,
    StudentSubject,
    ClassSchedule,
    StudentClassAssignment,
    Attendance
)
from datetime import datetime

teacher = Blueprint("teacher", __name__)

# =========================
# DASHBOARD
# =========================
@teacher.route("/teacher/dashboard")
@login_required
def dashboard():

    classes = ClassSchedule.query.order_by(ClassSchedule.class_date.desc()).all()

    return render_template(
        "teacher/dashboard.html",
        classes=classes
    )

# =========================
# CREATE SUBJECT
# =========================
@teacher.route("/teacher/subject", methods=["GET", "POST"])
@login_required
def subjects():

    if request.method == "POST":

        name = request.form.get("name")

        if not name:
            flash("Subject name required")
            return redirect(url_for("teacher.subjects"))

        subject = Subject(name=name)
        db.session.add(subject)
        db.session.commit()

        flash("Subject Added")
        return redirect(url_for("teacher.subjects"))

    all_subjects = Subject.query.all()

    return render_template(
        "teacher/subject.html",
        subjects=all_subjects
    )

# =========================
# CREATE STUDENT
# =========================
@teacher.route("/teacher/add_student", methods=["GET", "POST"])
@login_required
def add_student():

    if request.method == "POST":

        name = request.form.get("name")
        student_code = request.form.get("student_code")
        selected_subjects = request.form.getlist("subjects")

        student = Student(
            name=name,
            student_code=student_code
        )

        db.session.add(student)
        db.session.commit()

        for subject_id in selected_subjects:

            ss = StudentSubject(
                student_id=student.id,
                subject_id=subject_id
            )

            db.session.add(ss)

        db.session.commit()

        flash("Student Added Successfully")
        return redirect(url_for("teacher.add_student"))

    subjects = Subject.query.all()

    return render_template(
        "teacher/add_student.html",
        subjects=subjects
    )

# =========================
# STUDENT SEARCH
# =========================
@teacher.route("/teacher/students")
@login_required
def students():

    search = request.args.get("search", "")

    if search:

        students = Student.query.filter(
            Student.name.ilike(f"%{search}%")
        ).all()

    else:
        students = Student.query.all()

    return render_template(
        "teacher/students.html",
        students=students,
        search=search
    )

# =========================
# CREATE CLASS
# =========================
@teacher.route("/teacher/create_class", methods=["GET", "POST"])
@login_required
def create_class():

    if request.method == "POST":

        subject_id = request.form.get("subject_id")
        class_date = request.form.get("class_date")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")

        subject = Subject.query.get(subject_id)

        # check overlapping
        selected_students = StudentSubject.query.filter_by(
            subject_id=subject_id
        ).all()

        conflict_students = []

        for ss in selected_students:

            existing_classes = StudentClassAssignment.query.filter_by(
                student_id=ss.student_id
            ).all()

            for ec in existing_classes:

                cls = ClassSchedule.query.get(ec.class_schedule_id)

                if str(cls.class_date) == class_date:

                    old_start = cls.start_time
                    old_end = cls.end_time

                    new_start = datetime.strptime(start_time, "%H:%M").time()
                    new_end = datetime.strptime(end_time, "%H:%M").time()

                    overlap = (
                        new_start < old_end and new_end > old_start
                    )

                    if overlap:
                        student = Student.query.get(ss.student_id)
                        conflict_students.append(student.name)

        if conflict_students:

            flash(
                "Time conflict for: " +
                ", ".join(conflict_students)
            )

            return redirect(url_for("teacher.create_class"))

        new_class = ClassSchedule(
            class_name=subject.name,
            subject_id=subject_id,
            class_date=datetime.strptime(class_date, "%Y-%m-%d"),
            start_time=datetime.strptime(start_time, "%H:%M").time(),
            end_time=datetime.strptime(end_time, "%H:%M").time()
        )

        db.session.add(new_class)
        db.session.commit()

        # auto assign students
        subject_students = StudentSubject.query.filter_by(
            subject_id=subject_id
        ).all()

        for ss in subject_students:

            assign = StudentClassAssignment(
                student_id=ss.student_id,
                class_schedule_id=new_class.id
            )

            db.session.add(assign)

        db.session.commit()

        flash("Class Created Successfully")
        return redirect(url_for("teacher.dashboard"))

    subjects = Subject.query.all()

    return render_template(
        "teacher/create_class.html",
        subjects=subjects
    )

# =========================
# TAKE ATTENDANCE
# =========================
@teacher.route("/teacher/attendance/<int:class_id>", methods=["GET", "POST"])
@login_required
def attendance(class_id):

    class_data = ClassSchedule.query.get(class_id)

    assignments = StudentClassAssignment.query.filter_by(
        class_schedule_id=class_id
    ).all()

    students = []

    for a in assignments:

        student = Student.query.get(a.student_id)
        students.append(student)

    if request.method == "POST":

        for student in students:

            status = request.form.get(f"status_{student.id}")

            attendance = Attendance(
                student_id=student.id,
                class_schedule_id=class_id,
                status=True if status == "Present" else False
            )

            db.session.add(attendance)

        db.session.commit()

        flash("Attendance Saved")

        return redirect(url_for("teacher.dashboard"))

    return render_template(
        "teacher/take_attendance.html",
        students=students,
        class_data=class_data
    )
