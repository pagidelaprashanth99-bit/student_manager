from flask import Blueprint, render_template, request, redirect, flash
from flask_login import login_required, current_user
from app.models import Attendance, Student, ClassSchedule
from app import db
from datetime import datetime, date, timedelta

student_bp = Blueprint("student", __name__, url_prefix="/student")

@student_bp.route("/")
@login_required
def dashboard():
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        flash("Student profile not found", "error")
        return redirect("/logout")
    
    # Get all attendance records for this student (only from ClassSchedule)
    records = Attendance.query.filter(
        Attendance.student_id == student.id,
        Attendance.class_schedule_id.isnot(None)
    ).order_by(Attendance.marked_at.desc()).all()
    
    # Get class names for records
    records_with_class = []
    for record in records:
        if record.class_schedule_id:
            schedule = ClassSchedule.query.get(record.class_schedule_id)
            records_with_class.append({
                'record': record,
                'class_name': schedule.class_name if schedule else f"Class #{record.class_schedule_id}"
            })

    # Calculate attendance based on ClassSchedule
    all_schedules = ClassSchedule.query.all()
    total_classes = len(all_schedules)
    present = Attendance.query.filter(
        Attendance.student_id == student.id,
        Attendance.status == True,
        Attendance.class_schedule_id.isnot(None)
    ).count()
    percentage = (present / total_classes) * 100 if total_classes > 0 else 0
    
    # Get all class schedules with their status
    # Note: We'll use a more lenient check - allow marking if date matches
    # The actual time validation will be done on the client side and server side with time window
    now = datetime.now()
    current_date = now.date()
    current_time = now.time()
    
    class_schedules = []
    for schedule in ClassSchedule.query.all():
        # Check if student already marked attendance for this class
        existing = Attendance.query.filter_by(
            student_id=student.id,
            class_schedule_id=schedule.id
        ).first()
        
        # More lenient check - if date matches, allow marking (time will be validated on submit)
        is_today = (schedule.class_date == current_date) if schedule.class_date else False
        
        # Check if within time window (5 min before to 30 min after)
        if is_today and schedule.class_date:
            class_start = datetime.combine(schedule.class_date, schedule.start_time)
            class_end = datetime.combine(schedule.class_date, schedule.end_time)
            current_datetime = datetime.combine(current_date, current_time)
            window_start = class_start - timedelta(minutes=5)
            window_end = class_end + timedelta(minutes=30)
            is_during_class = window_start <= current_datetime <= window_end
        else:
            is_during_class = False
        
        can_mark = is_today and is_during_class and not existing
        
        class_schedules.append({
            'schedule': schedule,
            'is_today': is_today,
            'is_during_class': is_during_class,
            'can_mark': can_mark,
            'already_marked': existing is not None
        })

    return render_template(
        "student/dashboard.html",
        records=records_with_class,
        percentage=round(percentage, 2),
        class_schedules=class_schedules,
        current_time=current_time.strftime('%H:%M')
    )

@student_bp.route("/mark-attendance", methods=["POST"])
@login_required
def mark_attendance():
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        flash("Student profile not found", "error")
        return redirect("/logout")
    
    class_schedule_id = request.form.get("class_schedule_id")
    
    if not class_schedule_id:
        flash("Invalid class selection", "error")
        return redirect("/student")
    
    schedule = ClassSchedule.query.get(class_schedule_id)
    if not schedule:
        flash("Class schedule not found", "error")
        return redirect("/student")
    
    # Get client time from form if provided (for timezone handling)
    client_date_str = request.form.get("client_date")
    client_time_str = request.form.get("client_time")
    
    # Use client time if provided, otherwise fall back to server time
    if client_date_str and client_time_str:
        try:
            # Parse client date and time
            client_datetime = datetime.strptime(f"{client_date_str} {client_time_str}", "%Y-%m-%d %H:%M")
            current_date = client_datetime.date()
            current_time = client_datetime.time()
        except:
            # If parsing fails, use server time
            now = datetime.now()
            current_date = now.date()
            current_time = now.time()
    else:
        # Use server time as fallback
        now = datetime.now()
        current_date = now.date()
        current_time = now.time()
    
    if not schedule.class_date:
        flash("Class schedule date is not set!", "error")
        return redirect("/student")
    
    # More lenient date check - allow same day in any timezone
    schedule_date = schedule.class_date
    
    # Check if dates match (allowing for timezone differences)
    if schedule_date != current_date:
        flash(f"Class is scheduled for {schedule_date.strftime('%Y-%m-%d')}, but your current date is {current_date.strftime('%Y-%m-%d')}. Please mark attendance on the scheduled date.", "error")
        return redirect("/student")
    
    # More lenient time check - allow 5 minutes before and 30 minutes after class time
    start_time = schedule.start_time
    end_time = schedule.end_time
    
    # Create datetime objects for comparison (using today's date)
    class_start = datetime.combine(current_date, start_time)
    class_end = datetime.combine(current_date, end_time)
    current_datetime = datetime.combine(current_date, current_time)
    
    # Allow 5 minutes before class starts and 30 minutes after class ends
    window_start = class_start - timedelta(minutes=5)
    window_end = class_end + timedelta(minutes=30)
    
    if not (window_start <= current_datetime <= window_end):
        flash(f"Class time is {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}. Your current time is {current_time.strftime('%H:%M')}. Please mark attendance during class time (5 minutes before to 30 minutes after).", "error")
        return redirect("/student")
    
    # Check if already marked
    existing = Attendance.query.filter_by(
        student_id=student.id,
        class_schedule_id=schedule.id
    ).first()
    
    if existing:
        flash("You have already marked attendance for this class today!", "error")
        return redirect("/student")
    
    # Create attendance record
    # Use current datetime (from client or server)
    if client_date_str and client_time_str:
        try:
            marked_at = datetime.strptime(f"{client_date_str} {client_time_str}", "%Y-%m-%d %H:%M")
        except:
            marked_at = datetime.now()
    else:
        marked_at = datetime.now()
    
    attendance = Attendance(
        student_id=student.id,
        class_schedule_id=schedule.id,
        status=True,
        marked_at=marked_at
    )
    db.session.add(attendance)
    db.session.commit()
    
    flash(f"Attendance marked successfully for {schedule.class_name}!", "success")
    return redirect("/student")
