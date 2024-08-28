from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app import db, bcrypt
from app.forms import *
from app.models import *

auth = Blueprint('auth', __name__)

@auth.route("/register/student", methods=['GET', 'POST'])
def register_student():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = StudentRegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        student = Student(username=form.username.data, email=form.email.data, password=hashed_password, first_name=form.first_name.data, last_name=form.last_name.data)
        db.session.add(student)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('auth.student_login'))
    return render_template('register.html', title='Register as Student', form=form)

@auth.route("/register/creator", methods=['GET', 'POST'])
def register_creator():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = CreatorRegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        creator = CourseCreator(username=form.username.data, email=form.email.data, password=hashed_password, first_name=form.first_name.data, last_name=form.last_name.data)
        db.session.add(creator)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('auth.coursecreator_login'))
    return render_template('register.html', title='Register as Creator', form=form)

@auth.route('/student/login', methods=['GET', 'POST'])
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
    return render_template('student_login.html', form=form)

@auth.route('/coursecreator/login', methods=['GET', 'POST'])
def coursecreator_login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = CourseCreatorLoginForm()
    if form.validate_on_submit():
        coursecreator = CourseCreator.query.filter_by(email=form.email.data).first()
        if coursecreator and coursecreator.check_password(form.password.data):
            login_user(coursecreator)
            flash('Login successful!', 'success')
            return redirect(url_for('main.creator_dashboard'))
        else:
            flash('Login unsuccessful. Please check your email and password.', 'danger')
    return render_template('coursecreator_login.html', form=form)

@auth.route("/logout")
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))
