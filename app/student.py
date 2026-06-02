
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

    # Get logged-in student
    student_data = Student.query.filter_by(
        user_id=current_user.id
    ).first()

    result = []

    if student_data:

        # Get assigned classes for this student
        assignments = StudentClassAssignment.query.filter_by(
            student_id=student_data.id
        ).all()

        subjects = {}

        for assignment in assignments:

            class_schedule = ClassSchedule.query.get(
                assignment.class_schedule_id
            )

            if not class_schedule:
                continue

            subject_name = class_schedule.class_name

            # Create subject entry
            if subject_name not in subjects:

                subjects[subject_name] = {
                    "subject": subject_name,
                    "attended": 0,
                    "total": 0,
                    "percentage": 0,
                }

            # Increase total classes
            subjects[subject_name]["total"] += 1

            # Check attendance
            attendance = Attendance.query.filter_by(
                student_id=student_data.id,
                class_schedule_id=class_schedule.id,
                status=True
            ).first()

            if attendance:
                subjects[subject_name]["attended"] += 1

        # Calculate percentage
        for subject_name, data in subjects.items():

            if data["total"] > 0:

                data["percentage"] = round(
                    (data["attended"] / data["total"]) * 100,
                    2
                )

            # Manual override by teacher
            override = AttendancePercentageOverride.query.filter_by(
                student_id=student_data.id,
                subject_name=subject_name
            ).first()

            if override:
                data["percentage"] = override.percentage

            result.append(data)

    return render_template(
        "student/dashboard.html",
        result=result
    )
```
