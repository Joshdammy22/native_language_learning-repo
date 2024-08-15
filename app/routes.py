from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from .models import Student, CourseCreator, Course, Lesson, UserProgress, Quiz
from .forms import RegistrationForm, LoginForm, QuizForm
from . import db, bcrypt

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')


@main.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = None
        if 'creator' in request.form:
            user = CourseCreator(username=form.username.data, email=form.email.data, password=hashed_password, first_name=form.first_name.data, last_name=form.last_name.data)
        else:
            user = Student(username=form.username.data, email=form.email.data, password=hashed_password, first_name=form.first_name.data, last_name=form.last_name.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@main.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Student.query.filter_by(email=form.email.data).first() or CourseCreator.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            return redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route("/courses")
def courses():
    courses = Course.query.all()
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

@main.route("/dashboard")
@login_required
def dashboard():
    user_progress = UserProgress.query.filter_by(student_id=current_user.id).all()
    return render_template('dashboard.html', progress=user_progress)

@main.route("/quiz/<int:quiz_id>", methods=['GET', 'POST'])
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    form = QuizForm(quiz)
    if form.validate_on_submit():
        score = sum([1 for question in quiz.questions if form.questions[question.id].data == question.correct_choice_id])
        flash(f'You scored {score} out of {len(quiz.questions)}', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('quiz.html', title=quiz.title, form=form)
