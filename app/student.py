from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Student, StudentClassAssignment, ClassSchedule, Attendance

student = Blueprint("student", __name__)

@student.route("/student/dashboard")
@login_required
def dashboard():

    student_data = Student.query.filter_by(
        user_id=current_user.id
    ).first()

    classes = []
    attendance_records = []

    if student_data:

        assignments = StudentClassAssignment.query.filter_by(
            student_id=student_data.id
        ).all()

        for assignment in assignments:
            class_data = ClassSchedule.query.get(
                assignment.class_schedule_id
            )

            if class_data:
                classes.append(class_data)

        attendance_records = Attendance.query.filter_by(
            student_id=student_data.id
        ).all()

    return render_template(
        "student/dashboard.html",
        student=student_data,
        classes=classes,
        attendance_records=attendance_records
    )
