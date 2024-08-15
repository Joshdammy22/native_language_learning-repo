from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

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

    def __repr__(self):
        return f"Student('{self.first_name} {self.last_name}', '{self.username}', '{self.email}')"

class CourseCreator(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    courses = db.relationship('Course', backref='creator', lazy=True)  # Relationship to manage created courses

    def __repr__(self):
        return f"CourseCreator('{self.first_name} {self.last_name}', '{self.username}', '{self.email}')"

class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    courses = db.relationship('Course', backref='language', lazy=True)

    def __repr__(self):
        return f"Language('{self.name}')"

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=False)
    image_file = db.Column(db.String(20), nullable=True, default='default_course.jpg')  # Optional image
    video_url = db.Column(db.String(200), nullable=True)  # Optional video URL
    lessons = db.relationship('Lesson', backref='course', lazy=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('course_creator.id'), nullable=False)  # Reference to creator

    def __repr__(self):
        return f"Course('{self.title}', '{self.language.name}')"

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(20), nullable=True, default='default_lesson.jpg')  # Optional image
    video_url = db.Column(db.String(200), nullable=True)  # Optional video URL
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    def __repr__(self):
        return f"Lesson('{self.title}', '{self.course.title}')"

class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"UserProgress(Student: '{self.student_id}', Lesson: '{self.lesson_id}', Completed: {self.completed})"

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    questions = db.relationship('Question', backref='quiz', lazy=True)

    def __repr__(self):
        return f"Quiz('{self.title}')"

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(255), nullable=False)
    choices = db.relationship('Choice', backref='question', lazy=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    correct_choice_id = db.Column(db.Integer, db.ForeignKey('choice.id'), nullable=False)

    def __repr__(self):
        return f"Question('{self.question_text}')"

class Choice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    choice_text = db.Column(db.String(255), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)

    def __repr__(self):
        return f"Choice('{self.choice_text}')"
