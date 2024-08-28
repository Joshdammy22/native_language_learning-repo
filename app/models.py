from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

bcrypt = Bcrypt()

@login_manager.user_loader
def load_user(user_id):
    # Assuming user_id is either a Student or CourseCreator ID
    return Student.query.get(int(user_id)) or CourseCreator.query.get(int(user_id))

class Student(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    progress = db.relationship('UserProgress', backref='student', lazy=True)
    enrollments = db.relationship('Enrollment', backref='student', lazy=True)
    ratings = db.relationship('Rating', backref='student', lazy=True)

    @property
    def is_student(self):
        return True

    @property
    def is_course_creator(self):
        return False

    def __repr__(self):
        return f"Student('{self.first_name} {self.last_name}', '{self.username}', '{self.email}')"

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    
    def has_access_to_lesson(self, lesson):
        # Example logic: Check if the student is enrolled in the course associated with the lesson
        return any(enrollment.course_id == lesson.course_id for enrollment in self.enrollments)

class CourseCreator(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    courses = db.relationship('Course', backref='creator', lazy=True)

    @property
    def is_student(self):
        return False

    @property
    def is_course_creator(self):
        return True

    def __repr__(self):
        return f"CourseCreator('{self.first_name} {self.last_name}', '{self.username}', '{self.email}')"

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    demographics = db.Column(db.Text, nullable=True)
    history = db.Column(db.Text, nullable=True)
    courses = db.relationship('Course', backref='language', lazy=True)
    image_file = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return f"Language('{self.name}')"

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=False)
    image_file = db.Column(db.String(20), nullable=True, default='default_course.jpg')
    video_url = db.Column(db.String(200), nullable=True)
    lessons = db.relationship('Lesson', backref='course', lazy=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('course_creator.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, onupdate=datetime.utcnow)  

    def get_completion_rate(self):
        total_students = Enrollment.query.filter_by(course_id=self.id).count()
        completed_students = Enrollment.query.filter_by(course_id=self.id, completed=True).count()
        return (completed_students / total_students) * 100 if total_students > 0 else 0
    
    def get_average_rating(self):
        ratings = Rating.query.filter_by(course_id=self.id).all()
        if ratings:
            total_rating = sum([rating.rating for rating in ratings])
            return total_rating / len(ratings)
        return None

    def __repr__(self):
        return f"Course('{self.title}', '{self.language.name}')"

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text, nullable=True)
    date_rated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Rating {self.id}, Student {self.student_id}, Course {self.course_id}, Rating {self.rating}>'

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    objective = db.Column(db.String(600), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(20), nullable=True, default='default_lesson.jpg')
    video_url = db.Column(db.String(200), nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    user_progress = db.relationship('UserProgress', backref='lesson', lazy=True)

    def __repr__(self):
        return f"Lesson('{self.title}', '{self.course.title}')"

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    progress = db.Column(db.Float, nullable=False, default=0.0)  # Progress as a percentage
    grade = db.Column(db.Float, nullable=True)  # Grade can be null if not yet assigned
    completed = db.Column(db.Boolean, default=False)  # Whether the course is completed

    def __repr__(self):
        return f"Enrollment(student_id={self.student_id}, course_id={self.course_id}, progress={self.progress}, grade={self.grade})"

class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    time_spent = db.Column(db.Integer, nullable=True, default=0)  # Time spent on the lesson in seconds
    scrolled_to_bottom = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"UserProgress(Student: '{self.student_id}', Lesson: '{self.lesson_id}', Completed: {self.completed}, Time Spent: {self.time_spent}, Scrolled to Bottom: {self.scrolled_to_bottom})"
    
class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    questions = db.relationship('Question', backref='quiz', lazy=True)

    def __repr__(self):
        return f"Quiz('{self.title}')"

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String, nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)

    # Define the relationship to Choice explicitly
    choices = relationship('Choice', foreign_keys='Choice.question_id', backref='question', cascade='all, delete-orphan')

class Choice(db.Model):
    __tablename__ = 'choices'
    id = db.Column(db.Integer, primary_key=True)
    choice_text = db.Column(db.String, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
