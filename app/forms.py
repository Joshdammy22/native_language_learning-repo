from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, FileField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_wtf.file import FileAllowed
from .models import Quiz, Question, Choice

# Form for Registration (Student and Course Creator)
class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

# Form for Login (Student and Course Creator)
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Form for Course Creation
class CourseCreationForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    language = StringField('Language', validators=[DataRequired()])
    image_file = FileField('Course Image', validators=[FileAllowed(['jpg', 'png'])])
    video_url = StringField('Video URL')
    submit = SubmitField('Create Course')

# Form for Lesson Creation
class LessonCreationForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=100)])
    content = TextAreaField('Content', validators=[DataRequired()])
    image_file = FileField('Lesson Image', validators=[FileAllowed(['jpg', 'png'])])
    video_url = StringField('Video URL')
    submit = SubmitField('Create Lesson')

# Form for Quiz Creation
class QuizCreationForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=100)])
    lesson_id = StringField('Lesson ID', validators=[DataRequired()])
    submit = SubmitField('Create Quiz')

# Form for Question Creation
class QuestionCreationForm(FlaskForm):
    question_text = StringField('Question Text', validators=[DataRequired(), Length(min=2, max=255)])
    submit = SubmitField('Add Question')

# Form for Choice Creation
class ChoiceCreationForm(FlaskForm):
    choice_text = StringField('Choice Text', validators=[DataRequired(), Length(min=1, max=255)])
    correct = RadioField('Correct', choices=[('1', 'Yes'), ('0', 'No')], default='0')
    submit = SubmitField('Add Choice')

# Form for Quiz Submission
class QuizForm(FlaskForm):
    def __init__(self, quiz, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.questions = [RadioField(question.question_text, choices=[(choice.id, choice.choice_text) for choice in question.choices], default=question.correct_choice_id) for question in quiz.questions]
    submit = SubmitField('Submit Quiz')
