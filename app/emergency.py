from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from werkzeug.utils import secure_filename
from app import db
from app.models import (
    Student,
    Attendance,
    ClassSchedule
)
import os
from datetime import datetime

emergency = Blueprint("emergency", __name__)

# ===================================
# EMERGENCY HOME
# ===================================
@emergency.route("/teacher/emergency")
@login_required
def emergency_home():

    students = Student.query.all()

    return render_template(
        "emergency.html",
        students=students
    )

# ===================================
# MEDICAL ATTENDANCE
# ===================================
@emergency.route(
    "/teacher/emergency/student/<int:student_id>",
    methods=["GET", "POST"]
)
@login_required
def medical_attendance(student_id):

    student = Student.query.get(student_id)

    attendance_records = Attendance.query.filter_by(
        student_id=student_id
    ).all()

    if request.method == "POST":

        attendance_id = request.form.get("attendance_id")

        attendance = Attendance.query.get(attendance_id)

        attendance.status = True
        attendance.updated_by_emergency = True

        file = request.files.get("medical_report")

        if file and file.filename != "":

            filename = secure_filename(file.filename)

            save_path = os.path.join(
                current_app.config["UPLOAD_FOLDER"],
                filename
            )

            file.save(save_path)

            attendance.medical_report_path = filename

        db.session.commit()

        flash("Medical Attendance Updated")

        return redirect(
            url_for(
                "emergency.medical_attendance",
                student_id=student_id
            )
        )

    return render_template(
        "medical_attendance.html",
        student=student,
        attendance_records=attendance_records
    )

# ===================================
# CHANGE CLASS TIMINGS
# ===================================
@emergency.route(
    "/teacher/emergency/change_class",
    methods=["GET", "POST"]
)
@login_required
def change_class():

    classes = ClassSchedule.query.all()

    if request.method == "POST":

        class_id = request.form.get("class_id")

        class_data = ClassSchedule.query.get(class_id)

        new_date = request.form.get("class_date")
        new_start = request.form.get("start_time")
        new_end = request.form.get("end_time")

        class_data.class_date = datetime.strptime(
            new_date,
            "%Y-%m-%d"
        )

        class_data.start_time = datetime.strptime(
            new_start,
            "%H:%M"
        ).time()

        class_data.end_time = datetime.strptime(
            new_end,
            "%H:%M"
        ).time()

        db.session.commit()

        flash("Class Timing Updated")

        return redirect(
            url_for("emergency.change_class")
        )

    return render_template(
        "emergency_change_class.html",
        classes=classes
    )
