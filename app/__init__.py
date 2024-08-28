from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_caching import Cache
from flask_cors import CORS
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect  # Import CSRFProtect
from flask import request

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.student_login'
login_manager.session_protection = 'strong'
login_manager.login_message_category = "info"
mail = Mail()
cache = Cache()
cors = CORS()
migrate = Migrate()  # Create an instance of Migrate
csrf = CSRFProtect()  # Create an instance of CSRFProtect

def csrf_exempt(f):
    def decorated_function(*args, **kwargs):
        # Temporarily disable CSRF protection
        if request.method in ['POST', 'PUT', 'DELETE']:
            csrf._disable_on_request()
        return f(*args, **kwargs)
    return decorated_function





def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('config.Config')
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    cache.init_app(app)
    cors.init_app(app)
    migrate.init_app(app, db)  # Initialize Flask-Migrate
    csrf.init_app(app)  # Initialize CSRF protection
    
    # Import and register blueprints
    from .routes import main
    from app.auth.routes import auth
    from app.students.routes import students
    from app.creators.routes import creators
    from app.courses.routes import courses

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(students, url_prefix='/students')
    app.register_blueprint(creators, url_prefix='/creators')
    app.register_blueprint(courses, url_prefix='/courses')

    
    # Create the database tables if they don't exist
    with app.app_context():
        db.create_all()

    return app
