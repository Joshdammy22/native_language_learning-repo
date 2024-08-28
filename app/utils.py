from werkzeug.utils import secure_filename
import os
from flask import current_app

def save_image(image):
    if image:
        filename = secure_filename(image.filename)
        upload_folder = os.path.join('static', 'course_images')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        image_path = os.path.join(upload_folder, filename)
        print(f"Saving image to: {image_path}")  # Debugging line
        image.save(image_path)
        return filename
    return None

