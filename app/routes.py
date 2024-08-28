from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from .models import *
from .forms import *
from . import db, bcrypt
from .utils import save_image
from flask import jsonify
from werkzeug.utils import secure_filename
import os
from flask import session


main = Blueprint('main', __name__)


@main.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('main.authenticated_home'))
    else:
        return render_template('landing_page.html')

@main.route('/home')
@login_required
def authenticated_home():
    if not current_user.is_authenticated:
        return redirect(url_for('main.landing_page'))

    # Fetch featured courses
    courses = Course.query.all()
    
    # Sort courses by average rating
    sorted_courses = sorted(courses, key=lambda course: course.get_average_rating() or 0, reverse=True)
    
    # Limit the number of featured courses to 5
    featured_courses = sorted_courses[:5]

    # Fetch all languages
    languages = Language.query.all()

    # Fetch user progress
    user_progress = UserProgress.query.filter_by(student_id=current_user.id).all()

    return render_template('home.html', 
                           featured_courses=featured_courses,
                           languages=languages,
                           user_progress=user_progress)


@main.route('/search', methods=['GET'])
def search_courses():
    query = request.args.get('q')  # Use 'q' because the input field in the form uses name="q"
    if query:
        # Perform search by matching course title or description
        courses = Course.query.filter(
            (Course.title.ilike(f'%{query}%')) | 
            (Course.description.ilike(f'%{query}%'))
        ).all()
    else:
        courses = []
    
    return render_template('search_results.html', courses=courses, query=query)

@main.route("/courses")
def courses():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.student_login'))
    
    courses = Course.query.all()
    return render_template('courses.html', courses=courses)

from app import csrf_exempt
@csrf_exempt
@main.route('/course/<int:course_id>', methods=['GET', 'POST'])
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
        if form.validate_on_submit():
            if not enrolled:
                new_enrollment = Enrollment(student_id=current_user.id, course_id=course.id)
                db.session.add(new_enrollment)
                db.session.commit()
                enrolled = True  # Update the enrollment status
                return '', 204  # Respond with a no content status (for fetch API to handle)

    return render_template('course_detail.html', course=course, enrolled=enrolled, form=form, is_student=is_student)




@main.route('/course/learning/<int:course_id>')
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



@main.route('/language/<int:language_id>')
def language_detail(language_id):
    # Get the language object based on language_id or 404 if not found
    language = Language.query.get_or_404(language_id)
    
    # Retrieve all courses related to the language
    courses = language.courses  # This assumes that a backref or relationship is set up in your models

    # Pass the language and its courses to the template
    return render_template('language_detail.html', language=language, courses=courses)




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
        # Check if the input matches either an email or a username
        student = Student.query.filter(
            (Student.email == form.username_or_email.data) | 
            (Student.username == form.username_or_email.data)
        ).first()
        
        if student and student.check_password(form.password.data):
            login_user(student)
            flash('Login successful!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Login unsuccessful. Please check your credentials.', 'danger')
    elif form.errors:
        flash('Please correct the errors in the form and try again.', 'danger')

    return render_template('student_login.html', form=form)



@main.route('/coursecreator/login', methods=['GET', 'POST'])
def coursecreator_login():
    if current_user.is_authenticated:
        if current_user.is_course_creator:
            return redirect(url_for('main.creator_dashboard'))
        else:
            return redirect(url_for('main.home'))

    form = CourseCreatorLoginForm()
    if form.validate_on_submit():
        coursecreator = CourseCreator.query.filter(
            (CourseCreator.email == form.username_or_email.data) | 
            (CourseCreator.username == form.username_or_email.data)
        ).first()
        if coursecreator and coursecreator.check_password(form.password.data):
            login_user(coursecreator)
            flash('Login successful!', 'success')
            return redirect(url_for('main.creator_dashboard'))
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

    return render_template('creator_dashboard.html', 
                           total_courses=total_courses,
                           total_enrollments=total_enrollments,
                           average_rating=average_rating,
                           courses=courses)  # Pass the actual Course objects




@main.route("/dashboard")
@login_required
def student_dashboard():
    if not current_user.is_student:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))

    # Fetch enrollments
    enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
    enrolled_courses = [Course.query.get(e.course_id) for e in enrollments]
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
    grades = [e.grade for e in enrollments if e.grade is not None]
    average_grade = sum(grades) / len(grades) if grades else 0

    # Calculate current progress as the ratio of completed courses to enrolled courses
    total_enrolled_courses = len(enrolled_courses)
    total_completed_courses = len(completed_courses)
    current_progress = total_completed_courses / total_enrolled_courses if total_enrolled_courses > 0 else 0

    return render_template(
        'dashboard.html',
        enrolled_courses=enrolled_courses,
        course_progress=course_progress,
        completed_courses=len(completed_courses),
        average_grade=average_grade,
        current_progress=current_progress
    )


@main.route("/logout")
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))



@main.route("/create_course", methods=['GET', 'POST'])
@login_required
def create_course():
    form = CourseCreationForm()

    if form.validate_on_submit():
        # Fetch the selected language by its ID
        language = Language.query.get(form.language.data)
        if not language:
            flash('Invalid language selection', 'danger')
            return redirect(url_for('main.create_course'))

        # Save the image file if provided, otherwise use default
        image_file = save_image(form.image_file.data) if form.image_file.data else 'default_course.jpg'

        # Create a new Course instance
        new_course = Course(
            title=form.title.data,
            description=form.description.data,
            language_id=language.id,  # Correctly assign language_id
            image_file=image_file,
            video_url=form.video_url.data,
            creator_id=current_user.id  # Correctly assign creator_id
        )

        # Add the new course to the session and commit to the database
        db.session.add(new_course)
        db.session.commit()

        # Store the course ID and lesson count in the session to use in lesson creation
        session['course_id'] = new_course.id
        session['lesson_count'] = form.lesson_count.data

        # Flash success message and redirect to the lesson creation page
        flash(f'Course "{new_course.title}" has been created successfully! Now add lessons.', 'success')
        return redirect(url_for('main.add_lessons', course_id=new_course.id, lesson_index=1, lesson_count=form.lesson_count.data))

    # Render the course creation template with the form
    return render_template('create_course.html', title='Create Course', form=form)



@main.route("/course/<int:course_id>/lessons/<int:lesson_index>/add", methods=['GET', 'POST'])
@login_required
def add_lessons(course_id, lesson_index):
    course = Course.query.get_or_404(course_id)
    if course.creator_id != current_user.id:
        abort(403)

    # Retrieve lesson_count from query parameters
    lesson_count = request.args.get('lesson_count', type=int, default=0)

    # Validate lesson_index
    if lesson_index < 1 or lesson_index > lesson_count:
        abort(404)

    form = LessonCreationForm()

    if form.validate_on_submit():
        # Save lesson image if provided
        image_file = save_image(form.image_file.data) if form.image_file.data else None

        # Create and save lesson
        lesson = Lesson(
            title=form.title.data,
            objective=form.objective.data,
            content=form.content.data,
            image_file=image_file,
            video_url=form.video_url.data,
            course_id=course.id
        )
        db.session.add(lesson)
        db.session.commit()

        flash(f'Lesson {lesson_index} has been created!', 'success')

        # Determine next lesson index
        next_lesson_index = lesson_index + 1
        if next_lesson_index <= lesson_count:
            return redirect(url_for('main.add_lessons', course_id=course_id, lesson_index=next_lesson_index, lesson_count=lesson_count))
        else:
            return redirect(url_for('main.creator_dashboard'))

    return render_template('add_lessons.html', title='Add Lesson', form=form, course=course, lesson_index=lesson_index, lesson_count=lesson_count)


@main.route("/course/<int:course_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    if course.creator_id != current_user.id:
        abort(403)
    
    form = CourseEditForm()
    
    # Ensure that the language field choices are set
    form.language.choices = [(lang.id, lang.name) for lang in Language.query.all()]

    if form.validate_on_submit():
        course.title = form.title.data
        course.description = form.description.data

        if form.image_file.data:
            course.image_file = save_image(form.image_file.data)
        
        course.video_url = form.video_url.data
        course.date_updated = datetime.utcnow()
        db.session.commit()
        
        flash('Your course has been updated!', 'success')
        return redirect(url_for('main.creator_dashboard'))
    
    # Prepopulate the form with existing course data
    form.title.data = course.title
    form.description.data = course.description
    form.video_url.data = course.video_url
    form.language.data = course.language_id  # Set the pre-filled value
    
    return render_template(
        'edit_course.html',
        title='Edit Course',
        form=form,
        course=course,
        legend='Edit Course'
    )




@main.route("/course/<int:course_id>/delete", methods=['POST'])
@login_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    if course.creator_id != current_user.id:
        abort(403)
    
    # Handle related lessons
    for lesson in course.lessons:
        db.session.delete(lesson)
    
    db.session.delete(course)
    db.session.commit()
    
    flash('Course and related lessons have been successfully deleted.', 'success')
    return redirect(url_for('main.creator_dashboard'))

@main.route('/course/<int:course_id>/lessons/<int:lesson_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_lesson(course_id, lesson_id):
    course = Course.query.get_or_404(course_id)
    lesson = Lesson.query.get_or_404(lesson_id)
    
    if lesson.course_id != course.id:
        flash('Invalid lesson for this course.', 'danger')
        return redirect(url_for('main.edit_course', course_id=course.id))
    
    form = LessonEditingForm()

    if form.validate_on_submit():
        lesson.title = form.title.data
        lesson.objective = form.objective.data
        lesson.content = form.content.data
        
        if form.image_file.data:
            lesson.image_file = save_picture(form.image_file.data)
        
        lesson.video_url = form.video_url.data
        
        db.session.commit()
        flash('The lesson has been updated!', 'success')
        return redirect(url_for('main.edit_course', course_id=course.id))
    
    elif request.method == 'GET':
        form.title.data = lesson.title
        form.objective.data = lesson.objective
        form.content.data = lesson.content
        form.video_url.data = lesson.video_url
    
    # Query the quizzes related to this lesson
    quizzes = Quiz.query.filter_by(lesson_id=lesson.id).all()
    
    return render_template('edit_lesson.html', title='Edit Lesson', form=form, course=course, lesson=lesson, quizzes=quizzes)
@main.route('/course/<int:course_id>/lessons/<int:lesson_id>/create_quiz', methods=['GET', 'POST'])
@login_required
def create_quiz(course_id, lesson_id):
    print(f"course_id: {course_id}, lesson_id: {lesson_id}")
    try:
        course = Course.query.get_or_404(course_id)
        lesson = Lesson.query.get_or_404(lesson_id)

        if lesson.course_id != course.id:
            flash('Invalid lesson for this course.', 'danger')
            return redirect(url_for('main.edit_course', course_id=course.id))

        form = QuizForm()  # Initialize the form

        if request.method == 'POST':
            if not form.validate_on_submit():
                flash('Form validation failed.', 'danger')
                return redirect(url_for('main.create_quiz', course_id=course_id, lesson_id=lesson_id))

            title = request.form.get('title')
            questions_data = request.form.getlist('questions[0][text]')
            question_count = len(questions_data)

            if not title:
                flash('Quiz title is required.', 'danger')
                return redirect(url_for('main.create_quiz', course_id=course_id, lesson_id=lesson_id))

            quiz = Quiz(title=title, lesson_id=lesson.id)
            db.session.add(quiz)
            db.session.flush()

            for question_idx in range(question_count):
                question_text = request.form.get(f'questions[{question_idx}][text]')
                if not question_text:
                    continue

                question = Question(
                    question_text=question_text,
                    quiz_id=quiz.id
                )
                db.session.add(question)
                db.session.flush()

                correct_option_idx = int(request.form.get(f'questions[{question_idx}][correctOption]', -1))

                for option_idx, option_text in enumerate(request.form.getlist(f'questions[{question_idx}][options][]')):
                    choice = Choice(
                        choice_text=option_text,
                        question_id=question.id
                    )
                    db.session.add(choice)
                    db.session.flush()

                    if option_idx + 1 == correct_option_idx:
                        question.correct_choice_id = choice.id

                db.session.add(question)

            db.session.commit()

            return jsonify({
                'success': True,
                'redirect_url': url_for('main.edit_course', course_id=course_id)
            })

    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()
        abort(400)

    return render_template('quiz_creation.html', course_id=course_id, lesson_id=lesson_id, course=course, lesson=lesson, form=form)


@main.route('/quiz/<int:quiz_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    form = QuizEditingForm()

    # Populate the form with the existing quiz data
    form.title.data = quiz.title

    for question in quiz.questions:
        question_form = form.questions.append_entry()
        question_form.text.data = question.question_text

        # Adding options to the question form
        question_form.correctOption.choices = [(opt.id, opt.text) for opt in question.choices]
        for option in question.choices:
            question_form.options.append_entry()
            question_form.options[-1].text.data = option.choice_text

    if form.validate_on_submit():
        quiz.title = form.title.data

        # Clear existing questions and options
        for question in quiz.questions:
            for choice in question.choices:
                db.session.delete(choice)
            db.session.delete(question)

        # Add updated questions and options
        for question_form in form.questions.entries:
            question = Question(
                question_text=question_form.text.data,
                quiz=quiz,
                correct_choice_id=question_form.correctOption.data
            )
            db.session.add(question)

            for option_form in question_form.options.entries:
                choice = Choice(
                    choice_text=option_form.text.data,
                    question=question
                )
                db.session.add(choice)

        db.session.commit()
        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('main.edit_lesson', lesson_id=quiz.lesson_id))

    return render_template('edit_quiz.html', form=form, quiz=quiz)


@main.route('/quiz/<int:quiz_id>/view')
@login_required
def view_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    return render_template('view_quiz.html', quiz=quiz)



@main.route('/course/<int:course_id>/lesson/<int:lesson_id>/quiz/<int:quiz_id>/question/create', methods=['GET', 'POST'])
@login_required
def create_question(course_id, lesson_id, quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    form = QuestionCreationForm()  # Assuming you have a form for adding questions
    if form.validate_on_submit():
        question = Question(
            question_text=form.question_text.data,
            quiz_id=quiz.id
        )
        db.session.add(question)
        db.session.commit()
        flash('Question added successfully!', 'success')
        return redirect(url_for('main.edit_lesson', course_id=course_id, lesson_id=lesson_id, quiz_id=quiz.id))
    
    return render_template('create_question.html', title='Add Questions', form=form, quiz=quiz)



@main.route('/course/<int:course_id>/lesson/<int:lesson_id>/quiz/<int:quiz_id>/question/<int:question_id>/choice/create', methods=['GET', 'POST'])
@login_required
def create_choice(course_id, lesson_id, quiz_id, question_id):
    form = ChoiceCreationForm()
    if form.validate_on_submit():
        choice = Choice(choice_text=form.choice_text.data, question_id=question_id)
        db.session.add(choice)
        db.session.commit()
        if form.correct.data == '1':
            question = Question.query.get(question_id)
            question.correct_choice_id = choice.id
            db.session.commit()
        flash('Choice added successfully!', 'success')
        return redirect(url_for('main.edit_question', course_id=course_id, lesson_id=lesson_id, quiz_id=quiz_id, question_id=question_id))
    return render_template('create_choice.html', form=form, course_id=course_id, lesson_id=lesson_id, quiz_id=quiz_id, question_id=question_id)


@main.route('/course/<int:course_id>/lesson/<int:lesson_id>/quiz/<int:quiz_id>/submit', methods=['GET', 'POST'])
@login_required
def submit_quiz(course_id, lesson_id, quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    form = QuizForm(quiz)
    if form.validate_on_submit():
        correct_answers = 0
        for question in quiz.questions:
            if form.questions[question.id].data == str(question.correct_choice_id):
                correct_answers += 1
        score = (correct_answers / len(quiz.questions)) * 100
        flash(f'You scored {score}%', 'success')
        return redirect(url_for('main.view_lesson', course_id=course_id, lesson_id=lesson_id))
    return render_template('submit_quiz.html', form=form, quiz=quiz, course_id=course_id, lesson_id=lesson_id)


from flask import jsonify, redirect, url_for

@main.route("/course/<int:course_id>/manage", methods=['GET', 'POST'])
@login_required
def manage_course(course_id):
    course = Course.query.get_or_404(course_id)
    if course.creator_id != current_user.id:
        abort(403)

    form = DeleteCourseForm()

    if request.method == 'POST' and form.validate_on_submit():
        db.session.delete(course)
        db.session.commit()
        return jsonify({
            'success': True,
            'redirect_url': url_for('main.creator_dashboard')  # Correct endpoint name
        })

    return render_template('manage_course.html', course=course, form=form)


@main.route("/course/<int:course_id>")
def lesson_list(course_id):
    course = Course.query.get_or_404(course_id)
    lessons = Lesson.query.filter_by(course_id=course_id).all()
    return render_template('lessons.html', course=course, lessons=lessons)

@main.route("/lesson/<int:lesson_id>", methods=["GET", "POST"])
@login_required
def lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    course = lesson.course
    
    progress = UserProgress.query.filter_by(student_id=current_user.id, lesson_id=lesson_id).first()

    if request.method == "POST":
        data = request.json
        time_spent = data.get("time_spent")
        scrolled_to_bottom = data.get("scrolled_to_bottom")

        if time_spent is not None and scrolled_to_bottom is not None:
            if time_spent >= 420:  # Updated time limit to 420 seconds (7 minutes)
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
                    "message": "You must spend at least 7 minutes and scroll to the bottom to complete this lesson."
                })
        else:
            return jsonify({
                "status": "error",
                "message": "Invalid data received."
            })

    # Render lesson template and pass relevant data
    return render_template('lessons.html', lesson=lesson, course=course, progress=progress)


@main.route("/mark_completed/<int:lesson_id>", methods=["POST"])
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

from flask import current_app

@main.route('/add_language', methods=['GET', 'POST'])
def add_language():
    form = LanguageForm()
    if form.validate_on_submit():
        if form.image_file.data:
            # Create the directory if it doesn't exist
            directory = os.path.join(current_app.root_path, 'static/images/languages')
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            # Save the image file
            image_file = os.path.join(directory, form.image_file.data.filename)
            form.image_file.data.save(image_file)
        
        # Create the new language instance
        language = Language(
            name=form.name.data,
            demographics=form.demographics.data,
            history=form.history.data,
            image_file=form.image_file.data.filename if form.image_file.data else None
        )
        db.session.add(language)
        db.session.commit()
        flash('Language added successfully!', 'success')
        return redirect(url_for('main.add_language'))
    
    return render_template('add_language.html', title='Add Language', form=form)


@main.route('/edit_language/<int:language_id>', methods=['GET', 'POST'])
def edit_language(language_id):
    language = Language.query.get_or_404(language_id)
    form = LanguageForm()

    if form.validate_on_submit():
        if form.image_file.data:
            directory = os.path.join(current_app.root_path, 'static/images/languages')
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            image_file = secure_filename(form.image_file.data.filename)
            form.image_file.data.save(os.path.join(directory, image_file))
            language.image_file = image_file
        
        language.name = form.name.data
        language.demographics = form.demographics.data
        language.history = form.history.data
        db.session.commit()
        flash('Language updated successfully!', 'success')
        return redirect(url_for('main.edit_language', language_id=language.id))

    elif request.method == 'GET':
        form.name.data = language.name
        form.demographics.data = language.demographics
        form.history.data = language.history

    return render_template('edit-language.html', title='Edit Language', form=form)