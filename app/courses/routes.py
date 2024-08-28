from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models import *
from app.forms import *
from app.utils import save_image
from app import db
from flask import session
from flask import render_template, jsonify, request, session, redirect, url_for


courses = Blueprint('courses', __name__)


from app import csrf_exempt
@csrf_exempt
@courses.route('/course/<int:course_id>', methods=['GET', 'POST'])
@login_required
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    form = EnrollmentForm()

    enrolled = False
    is_student = hasattr(current_user, 'is_student') and current_user.is_student

    if is_student:
    # Check if the current user is already enrolled in the course
        enrollment = Enrollment.query.filter_by(student_id=current_user.id, course_id=course_id).first()
        if enrollment:
            enrolled = True
            
        # Handle form submission
        if form.validate_on_submit() and not enrolled:
            new_enrollment = Enrollment(student_id=current_user.id, course_id=course.id)
            db.session.add(new_enrollment)
            db.session.commit()
            enrolled = True
            return '', 204

    return render_template('course_detail.html', course=course, enrolled=enrolled, form=form, is_student=is_student)

@courses.route("/course/learning/<int:course_id>")
@login_required
def course_learning(course_id):
    course = Course.query.get_or_404(course_id)
    
    # Ensure the user is enrolled in the course
    enrollment = Enrollment.query.filter_by(student_id=current_user.id, course_id=course_id).first()
    if not enrollment:
        flash('You must enroll in the course to access the content.', 'warning')
        return redirect(url_for('main.course_detail', course_id=course_id))
    
    # Get user's progress in the course by joining lessons with user progress
    user_progress = db.session.query(Lesson.id, UserProgress.completed).join(
        UserProgress, Lesson.id == UserProgress.lesson_id, isouter=True
    ).filter(
        Lesson.course_id == course_id,
        UserProgress.student_id == current_user.id
    ).all()
    
    # Extract completed lesson IDs
    completed_lesson_ids = {lesson_id for lesson_id, completed in user_progress if completed}
    
    # Calculate progress percentage
    total_lessons = len(course.lessons)
    completed_lessons = len(completed_lesson_ids)
    progress_percentage = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0
    
    # Mark lessons as completed
    for lesson in course.lessons:
        lesson.completed = lesson.id in completed_lesson_ids

    # Fetch notes related to this course (if applicable)
    #notes = Note.query.filter_by(course_id=course_id, student_id=current_user.id).all()
    notes = [ ]
    return render_template('course_learning.html', course=course, notes=notes, progress_percentage=progress_percentage)


@courses.route("/lesson/<int:lesson_id>", methods=["GET", "POST"])
@login_required
def lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    course = lesson.course  # Fetch the course associated with the lesson
    
    progress = UserProgress.query.filter_by(student_id=current_user.id, lesson_id=lesson_id).first()

    if request.method == "POST":
        data = request.json
        time_spent = data.get("time_spent")
        scrolled_to_bottom = data.get("scrolled_to_bottom")

        if time_spent >= 180 and scrolled_to_bottom:
            if not progress:
                progress = UserProgress(
                    student_id=current_user.id, 
                    lesson_id=lesson_id, 
                    completed=True
                )
                db.session.add(progress)
            else:
                progress.completed = True

            db.session.commit()

            return jsonify({
                "status": "success",
                "message": "Lesson marked as completed successfully."
            })
        else:
            return jsonify({
                "status": "error",
                "message": "You must spend at least 3 minutes and scroll to the bottom to complete this lesson."
            })

    return render_template('lessons.html', lesson=lesson, course=course)

@courses.route("/mark_completed/<int:lesson_id>", methods=["POST"])
@login_required
def mark_completed(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)

    if not current_user.has_access_to_lesson(lesson):
        return jsonify({'status': 'error', 'message': 'Unauthorized access'}), 403

    data = request.get_json()
    time_spent = data.get('time_spent', 0)
    scrolled_to_bottom = data.get('scrolled_to_bottom', False)

    # Mark the lesson as completed for the current user
    user_progress = UserProgress.query.filter_by(student_id=current_user.id, lesson_id=lesson_id).first()
    if user_progress:
        user_progress.completed = True
        user_progress.time_spent = time_spent
        user_progress.scrolled_to_bottom = scrolled_to_bottom
    else:
        user_progress = UserProgress(student_id=current_user.id, lesson_id=lesson_id, completed=True,
                                     time_spent=time_spent, scrolled_to_bottom=scrolled_to_bottom)
        db.session.add(user_progress)

    db.session.commit()

    # Find the next lesson
    next_lesson = Lesson.query.filter(Lesson.course_id == lesson.course_id, Lesson.id > lesson.id).order_by(Lesson.id).first()

    # Return a JSON response with the next lesson's URL
    if next_lesson:
        return jsonify({'status': 'success', 'message': 'Lesson marked as completed', 'next_lesson_url': url_for('main.lesson', lesson_id=next_lesson.id)}), 200
    else:
        return jsonify({'status': 'success', 'message': 'Lesson marked as completed', 'next_lesson_url': None}), 200



@courses.route("/create_course", methods=['GET', 'POST'])
@login_required
def create_course():
    form = CourseCreationForm()

    if form.validate_on_submit():
        language = Language.query.get(form.language.data)
        if not language:
            flash('Invalid language selection', 'danger')
            return redirect(url_for('courses.create_course'))

        image_file = save_image(form.image_file.data) if form.image_file.data else 'default_course.jpg'

        new_course = Course(
            title=form.title.data,
            description=form.description.data,
            language_id=language.id,
            image_file=image_file,
            video_url=form.video_url.data,
            creator_id=current_user.id
        )

        db.session.add(new_course)
        db.session.commit()

        session['course_id'] = new_course.id
        session['lesson_count'] = form.lesson_count.data

        flash(f'Course "{new_course.title}" has been created successfully! Now add lessons.', 'success')
        return redirect(url_for('courses.add_lessons', course_id=new_course.id, lesson_index=1, lesson_count=form.lesson_count.data))

    return render_template('create_course.html', title='Create Course', form=form)

@courses.route("/course/<int:course_id>/lessons/<int:lesson_index>/<int:lesson_count>", methods=['GET', 'POST'])
@login_required
def add_lessons(course_id, lesson_index, lesson_count):
    form = LessonCreationForm()

    if form.validate_on_submit():
        new_lesson = Lesson(
            title=form.title.data,
            content=form.content.data,
            course_id=course_id
        )

        db.session.add(new_lesson)
        db.session.commit()

        if lesson_index < lesson_count:
            next_index = lesson_index + 1
            return redirect(url_for('courses.add_lessons', course_id=course_id, lesson_index=next_index, lesson_count=lesson_count))

        flash('All lessons have been added.', 'success')
        return redirect(url_for('creators.creator_dashboard'))

    return render_template('add_lessons.html', title='Add Lessons', form=form, lesson_index=lesson_index, lesson_count=lesson_count)
