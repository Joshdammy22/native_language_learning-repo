from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, FileField, RadioField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_wtf.file import FileAllowed
from .models import *
from wtforms import StringField, TextAreaField, FileField, SelectField, URLField, SubmitField, IntegerField, HiddenField, BooleanField, FormField, FieldList
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from flask_wtf.file import FileAllowed
# Assuming you're using Flask-CKEditor
from flask_ckeditor import CKEditorField

# In your form definition
class CourseForm(FlaskForm):
    # Other fields...
    description = CKEditorField('Description', validators=[DataRequired()])

class StudentRegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=60)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register as Student')

    def validate_username(self, username):
        student = Student.query.filter_by(username=username.data).first()
        if student:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        student = Student.query.filter_by(email=email.data).first()
        if student:
            raise ValidationError('That email is already registered. Please choose a different one.')

class CreatorRegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=60)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register as Creator')

    def validate_username(self, username):
        creator = CourseCreator.query.filter_by(username=username.data).first()
        if creator:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        creator = CourseCreator.query.filter_by(email=email.data).first()
        if creator:
            raise ValidationError('That email is already registered. Please choose a different one.')


class StudentLoginForm(FlaskForm):
    username_or_email = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class CourseCreatorLoginForm(FlaskForm):
    username_or_email = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Form for Course Creation
class CourseCreationForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    language = SelectField('Language', validators=[DataRequired()])
    image_file = FileField('Course Image', validators=[FileAllowed(['jpg', 'png','jpeg'])])
    video_url = StringField('Video URL')
    lesson_count = IntegerField('How many lessons will the course have?', validators=[DataRequired(), NumberRange(min=1, message="The course must have at least one lesson.")])
    submit = SubmitField('Create Course')

    def __init__(self, *args, **kwargs):
        super(CourseCreationForm, self).__init__(*args, **kwargs)
        self.language.choices = [(l.id, l.name) for l in Language.query.all()]


# Form for Course Editing
class CourseEditForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    image_file = FileField('Image')
    video_url = URLField('Video URL')
    lesson_count = IntegerField('How many lessons will the course have?', validators=[
        DataRequired(),
        NumberRange(min=1, message="The course must have at least one lesson.")
    ])
    language = SelectField('Language', choices=[], coerce=int)
    submit = SubmitField('Update Course')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.language.choices = [(lang.id, lang.name) for lang in Language.query.all()]  # Set choices dynamically



class LessonCreationForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=100)])
    content = TextAreaField('Content', validators=[DataRequired()])
    image_file = FileField('Lesson Image', validators=[FileAllowed(['jpg', 'png','jpeg'])])
    video_url = StringField('Video URL')
    submit = SubmitField('Add Lesson')


class LessonEditingForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=100)])
    objective = TextAreaField('Learning Objective:', validators=[DataRequired(), Length(max=600)])
    content = TextAreaField('Content', validators=[DataRequired()])
    image_file = FileField('Lesson Image', validators=[FileAllowed(['jpg', 'png','jpeg'])])
    video_url = StringField('Video URL')
    submit = SubmitField('Update Lesson')

# Form for Course EDITING
class EditCourseForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    image_file = FileField('Course Image', validators=[FileAllowed(['jpg', 'png','jpeg'])])
    video_url = StringField('Video URL')
    submit = SubmitField('Update Course')


class LessonCreationForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=100)])
    objective = TextAreaField('Learning Objective:', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    image_file = FileField('Lesson Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    video_url = StringField('Video URL')
    submit = SubmitField('Create Lesson')


class QuizForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    lesson_id = IntegerField('Lesson ID', validators=[DataRequired()])
    submit = SubmitField('Save')


class QuestionForm(FlaskForm):
    question_text = StringField('Question Text', validators=[DataRequired()])
    submit = SubmitField('Save')

class ChoiceForm(FlaskForm):
    choice_text = StringField('Choice Text', validators=[DataRequired()])
    is_correct = BooleanField('Correct Choice')
    submit = SubmitField('Save')


# Form for Quiz Creation
class QuizCreationForm(FlaskForm):
    title = StringField('Quiz Title', validators=[DataRequired()])
    lesson_id = HiddenField('Lesson ID', validators=[DataRequired()])
    course_id = HiddenField('Course ID', validators=[DataRequired()])
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


class OptionForm(FlaskForm):
    text = StringField('Option', validators=[DataRequired()])

class QuestionForm(FlaskForm):
    text = StringField('Question Text', validators=[DataRequired()])
    options = FieldList(FormField(OptionForm), min_entries=1)
    correctOption = RadioField('Correct Option', choices=[])

class QuizEditingForm(FlaskForm):
    title = StringField('Quiz Title', validators=[DataRequired()])
    questions = FieldList(FormField(QuestionForm), min_entries=1)


class DeleteCourseForm(FlaskForm):
    submit = SubmitField('Delete')

class LanguageForm(FlaskForm):
    name = StringField('Language Name', validators=[DataRequired()])
    demographics = TextAreaField('Demographics', validators=[Optional()])
    history = TextAreaField('History', validators=[Optional()])
    image_file = FileField('Language Image', validators=[Optional()])
    submit = SubmitField('Add Language')

class EnrollmentForm(FlaskForm):
    pass  # No fields needed, just a form for CSRF protection

# class QuizForm(FlaskForm):
#     submit = SubmitField('Submit Quiz')

#     def __init__(self, quiz=None, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.questions = []
#         if quiz:
#             for idx, question in enumerate(quiz.questions):
#                 choices = [(choice.id, choice.choice_text) for choice in question.choices]
#                 field = RadioField(
#                     label=question.question_text,
#                     choices=choices,
#                     default=question.correct_choice_id if question.correct_choice_id else None,
#                     coerce=int
#                 )
#                 self.questions.append(field)
#                 setattr(self, f'question_{idx}', field)

                
# class QuizForm(FlaskForm):
#     submit = SubmitField('Submit Quiz')

#     def __init__(self, quiz=None, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.questions = []
#         if quiz:
#             for idx, question in enumerate(quiz.questions):
#                 choices = [(choice.id, choice.choice_text) for choice in question.choices]
#                 field = RadioField(
#                     label=question.question_text,
#                     choices=choices,
#                     default=question.correct_choice_id if question.correct_choice_id else None,
#                     coerce=int
#                 )
#                 self.questions.append(field)
#                 setattr(self, f'question_{idx}', field)

# class QuizEditingForm(FlaskForm):
#     title = StringField('Quiz Title', validators=[DataRequired()])
#     submit = SubmitField('Update Quiz')

#     def __init__(self, quiz=None, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.questions = []
#         self.question_fields = {}
#         self.correct_option_fields = {}

#         if quiz:
#             for idx, question in enumerate(quiz.questions):
#                 question_field = StringField(
#                     label=f'Question {idx + 1}',
#                     default=question.question_text,
#                     validators=[DataRequired()]
#                 )
#                 self.question_fields[f'question_{idx}'] = question_field
#                 setattr(self, f'question_{idx}', question_field)

#                 options = []
#                 for opt_idx, choice in enumerate(question.choices):
#                     option_field = StringField(
#                         label=f'Option {opt_idx + 1}',
#                         default=choice.choice_text,
#                         validators=[DataRequired()]
#                     )
#                     options.append(option_field)
#                     setattr(self, f'option_{idx}_{opt_idx}', option_field)

#                 correct_option_field = RadioField(
#                     label='Correct Option',
#                     choices=[(choice.id, f'Option {opt_idx + 1}') for opt_idx, choice in enumerate(question.choices)],
#                     default=question.correct_choice_id,
#                     coerce=int
#                 )
#                 self.correct_option_fields[f'correct_option_{idx}'] = correct_option_field
#                 setattr(self, f'correct_option_{idx}', correct_option_field)

#                 self.questions.append({
#                     'text': question_field,
#                     'options': options,
#                     'correct_option': correct_option_field
#                 })
