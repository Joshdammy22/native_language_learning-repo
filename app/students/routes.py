from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import *

students = Blueprint('students', __name__)

@students.route("/dashboard")
@login_required
def student_dashboard():
    if not current_user.is_student:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))

    # Fetch enrollments
    enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
    enrolled_courses = [Course.query.get(e.course_id) for e in enrollments]

    # Logic to calculate completed courses
    completed_courses = []
    course_progress = {}

    for course in enrolled_courses:
        lessons = course.lessons
        total_lessons = len(lessons)
        
        # Calculate the number of completed lessons for the course
        completed_lessons = sum(
            1 for lesson in lessons
            if UserProgress.query.filter_by(student_id=current_user.id, lesson_id=lesson.id, completed=True).first()
        )
        
        # Store progress information
        course_progress[course.id] = {
            'total': total_lessons,
            'completed': completed_lessons
        }

        # Mark course as completed if all lessons are completed
        if completed_lessons == total_lessons and total_lessons > 0:
            completed_courses.append(course)

    # Calculate average grade
    grades = [enrollment.grade for enrollment in enrollments if enrollment.grade is not None]
    average_grade = sum(grades) / len(grades) if grades else 0

    # Calculate current progress across all enrolled courses
    current_progress = sum(
        Enrollment.query.filter_by(student_id=current_user.id, course_id=course.id).first().progress
        for course in enrolled_courses if Enrollment.query.filter_by(student_id=current_user.id, course_id=course.id).first().progress is not None
    ) / len(enrolled_courses) if enrolled_courses else 0

    return render_template('dashboard.html', 
                           enrolled_courses=enrolled_courses,
                           course_progress=course_progress,
                           completed_courses=len(completed_courses),
                           average_grade=average_grade,
                           current_progress=current_progress)

@login_required
@students.route('/my-courses')
def my_courses():
    if not current_user.is_student:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    student_id = current_user.id
    enrollments = Enrollment.query.filter_by(student_id=student_id).all()
    courses_with_enrollments = [(enrollment, Course.query.get(enrollment.course_id)) for enrollment in enrollments]
    return render_template('my_courses.html', courses_with_enrollments=courses_with_enrollments)

@students.route("/completed_courses")
@login_required
def completed_courses():
    if not current_user.is_student:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))

    # Fetch enrollments
    enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
    enrolled_courses = [Course.query.get(e.course_id) for e in enrollments]

    # Logic to calculate completed courses
    completed_courses = []
    course_progress = {}

    for course in enrolled_courses:
        lessons = course.lessons
        total_lessons = len(lessons)
        
        # Calculate the number of completed lessons for the course
        completed_lessons = sum(
            1 for lesson in lessons
            if UserProgress.query.filter_by(student_id=current_user.id, lesson_id=lesson.id, completed=True).first()
        )
        
        # Store progress information
        course_progress[course.id] = {
            'total': total_lessons,
            'completed': completed_lessons
        }

        # Mark course as completed if all lessons are completed
        if completed_lessons == total_lessons and total_lessons > 0:
            completed_courses.append(course)

    return render_template('completed_courses.html', 
                           completed_courses=completed_courses,
                           course_progress=course_progress)
