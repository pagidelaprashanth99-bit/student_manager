from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import (
    Student,
    ClassSchedule,
    StudentClassAssignment,
    Attendance,
    AttendancePercentageOverride,
)

student = Blueprint("student", __name__, url_prefix="/student")


@student.route("/dashboard")
@login_required
def dashboard():
    student_data = Student.query.filter_by(user_id=current_user.id).first()

    result = []

    if student_data:
        assignments = StudentClassAssignment.query.filter_by(
            student_id=student_data.id
        ).all()

        subjects = {}

        for assignment in assignments:
            class_schedule = ClassSchedule.query.get(assignment.class_schedule_id)
            if not class_schedule:
                continue

            subject = class_schedule.class_name

            if subject not in subjects:
                subjects[subject] = {
                    "subject": subject,
                    "attended": 0,
                    "total": 0,
                    "percentage": 0,
                }

            subjects[subject]["total"] += 1

            attendance = Attendance.query.filter_by(
                student_id=student_data.id,
                class_schedule_id=class_schedule.id,
                status=True,
            ).first()

            if attendance:
                subjects[subject]["attended"] += 1

        for subject_name, data in subjects.items():
            if data["total"] > 0:
                data["percentage"] = round(
                    (data["attended"] / data["total"]) * 100, 2
                )

            override = AttendancePercentageOverride.query.filter_by(
                student_id=student_data.id,
                subject_name=subject_name,
            ).first()

            if override:
                data["percentage"] = override.percentage

            result.append(data)

    return render_template("student/dashboard.html", result=result)
