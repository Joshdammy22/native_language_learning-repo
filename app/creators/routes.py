from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import *

creators = Blueprint('creators', __name__)

@creators.route('/creator/dashboard')
@login_required
def creator_dashboard():
    if not current_user.is_course_creator:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))

    courses = Course.query.filter_by(creator_id=current_user.id).all()
    total_courses = len(courses)
    total_enrollments = sum([Enrollment.query.filter_by(course_id=course.id).count() for course in courses])
    total_ratings = sum([Rating.query.filter_by(course_id=course.id).count() for course in courses])
    average_rating = sum([course.get_average_rating() for course in courses]) / total_courses if total_ratings > 0 else 0

    return render_template('creator_dashboard.html', 
                           total_courses=total_courses,
                           total_enrollments=total_enrollments,
                           average_rating=average_rating,
                           courses=courses)
