from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_caching import Cache
from flask_cors import CORS
from flask_migrate import Migrate  # Import Flask-Migrate

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()
cache = Cache()
cors = CORS()
migrate = Migrate()  # Create an instance of Migrate

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
    
    # Import and register blueprints
    from .routes import main
    app.register_blueprint(main)
    
    # Create the database tables if they don't exist
    with app.app_context():
        db.create_all()


    return app
