from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') 
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
    CACHE_TYPE = 'simple'
    CORS_HEADERS = 'Content-Type'
    UPLOAD_FOLDER = 'static/course_images'
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
