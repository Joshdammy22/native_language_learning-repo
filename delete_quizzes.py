from app import create_app, db
from app.models import Quiz

app = create_app()  # or import your app instance if it's already created

with app.app_context():
    def delete_all_quizzes():
        try:
            quizzes = Quiz.query.all()

            for quiz in quizzes:
                db.session.delete(quiz)

            db.session.commit()
            print("All quizzes and their associated questions and choices have been deleted.")
        except Exception as e:
            db.session.rollback()
            print(f"An error occurred: {e}")

    delete_all_quizzes()
