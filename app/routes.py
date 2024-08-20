from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from .models import *
from .forms import *
from . import db, bcrypt

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route("/register/student", methods=['GET', 'POST'])
def register_student():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = StudentRegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        student = Student(username=form.username.data, email=form.email.data, password=hashed_password, first_name=form.first_name.data, last_name=form.last_name.data)
        db.session.add(student)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('main.student_login'))
    elif form.errors:
        flash('Please correct the errors in the form and try again.', 'danger')
    return render_template('register.html', title='Register as Student', form=form)

@main.route("/register/creator", methods=['GET', 'POST'])
def register_creator():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = CreatorRegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        creator = CourseCreator(username=form.username.data, email=form.email.data, password=hashed_password, first_name=form.first_name.data, last_name=form.last_name.data)
        db.session.add(creator)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('main.coursecreator_login'))
    elif form.errors:
        flash('Please correct the errors in the form and try again.', 'danger')
    return render_template('register.html', title='Register as Creator', form=form)



@main.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = StudentLoginForm()
    if form.validate_on_submit():
        student = Student.query.filter_by(email=form.email.data).first()
        if student and student.check_password(form.password.data):
            login_user(student)
            flash('Login successful!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Login unsuccessful. Please check your email and password.', 'danger')
    elif form.errors:
        flash('Please correct the errors in the form and try again.', 'danger')

    return render_template('student_login.html', form=form)

@main.route('/coursecreator/login', methods=['GET', 'POST'])
def coursecreator_login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = CourseCreatorLoginForm()
    if form.validate_on_submit():
        coursecreator = CourseCreator.query.filter_by(email=form.email.data).first()
        if coursecreator and coursecreator.check_password(form.password.data):
            login_user(coursecreator)
            flash('Login successful!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Login unsuccessful. Please check your email and password.', 'danger')
    elif form.errors:
        flash('Please correct the errors in the form and try again.', 'danger')

    return render_template('coursecreator_login.html', form=form)


@main.route('/creator/dashboard')
@login_required
def creator_dashboard():
    if not current_user.is_course_creator:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))

    # Fetch the total number of courses created by the current user
    courses = Course.query.filter_by(creator_id=current_user.id).all()
    total_courses = len(courses)

    # Fetch the total number of enrollments for all courses created by the current user
    total_enrollments = sum([Enrollment.query.filter_by(course_id=course.id).count() for course in courses])

    # Calculate the average rating for all courses created by the current user
    total_ratings = sum([Rating.query.filter_by(course_id=course.id).count() for course in courses])
    average_rating = 0
    if total_ratings > 0:
        average_rating = sum([course.get_average_rating() for course in courses]) / total_courses

    # Prepare data for each course
    course_data = []
    for course in courses:
        enrollments = Enrollment.query.filter_by(course_id=course.id).count()
        completion_rate = course.get_completion_rate()
        rating = course.get_average_rating()
        course_data.append({
            'name': course.name,
            'enrollments': enrollments,
            'completion_rate': completion_rate,
            'rating': rating,
        })

    return render_template('creator_dashboard.html', 
                           total_courses=total_courses,
                           total_enrollments=total_enrollments,
                           average_rating=average_rating,
                           courses=course_data)

@main.route("/dashboard")
@login_required
def student_dashboard():
    if not current_user.is_student:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))

    user_progress = UserProgress.query.filter_by(student_id=current_user.id).all()
    return render_template('dashboard.html', progress=user_progress)

@main.route("/logout")
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))


@main.route('/create_course', methods=['GET', 'POST'])
@login_required
def create_course():
    form = CreateCourseForm()
    
    # Populate the language choices from the Language model
    form.language.choices = [(lang.id, lang.name) for lang in Language.query.all()]
    
    if form.validate_on_submit():
        # Save the course to the database
        course = Course(
            title=form.title.data,
            description=form.description.data,
            language_id=form.language.data,
            creator_id=current_user.id
        )
        
        if form.image_file.data:
            # Handle the image upload here (code not provided)
            pass
        
        db.session.add(course)
        db.session.commit()
        
        flash('Your course has been created!', 'success')
        return redirect(url_for('main.creator_dashboard'))
    
    return render_template('create_course.html', title='Create Course', form=form)


@main.route("/courses")
def courses():
    try:
        courses = Course.query.all()
    except Exception as e:
        flash('An error occurred while fetching the courses. Please try again later.', 'danger')
        return redirect(url_for('main.home'))
    return render_template('courses.html', courses=courses)

@main.route("/course/<int:course_id>")
def lesson_list(course_id):
    course = Course.query.get_or_404(course_id)
    lessons = Lesson.query.filter_by(course_id=course_id).all()
    return render_template('lessons.html', course=course, lessons=lessons)

@main.route("/lesson/<int:lesson_id>")
@login_required
def lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    progress = UserProgress.query.filter_by(student_id=current_user.id, lesson_id=lesson_id).first()
    if not progress:
        progress = UserProgress(student_id=current_user.id, lesson_id=lesson_id, completed=True)
        db.session.add(progress)
        db.session.commit()
    return render_template('lesson.html', lesson=lesson)


@main.route("/quiz/<int:quiz_id>", methods=['GET', 'POST'])
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    form = QuizForm(quiz)
    if form.validate_on_submit():
        score = sum([1 for question in quiz.questions if form.questions[question.id].data == question.correct_choice_id])
        flash(f'You scored {score} out of {len(quiz.questions)}', 'success')
        return redirect(url_for('main.dashboard'))
    elif form.errors:
        flash('An error occurred while submitting the quiz. Please try again.', 'danger')
    return render_template('quiz.html', title=quiz.title, form=form)
