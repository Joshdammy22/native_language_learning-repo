import sys
import os

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Language

# Create the app and the database
app = create_app()
app.app_context().push()

# Define the languages to populate
languages = [
    {'name': 'Hausa', 'description': 'A Chadic language spoken in northern Nigeria and Niger.'},
    {'name': 'Yoruba', 'description': 'A Niger-Congo language spoken in southwestern Nigeria.'},
    {'name': 'Igbo', 'description': 'A Bantu language spoken in southeastern Nigeria.'},
    {'name': 'Fulani', 'description': 'A West African language spoken across the Sahel.'},
    {'name': 'Kanuri', 'description': 'A Nilo-Saharan language spoken in northeastern Nigeria.'},
    {'name': 'Tiv', 'description': 'A Bantu language spoken in central Nigeria.'},
    {'name': 'Idoma', 'description': 'A Niger-Congo language spoken in central Nigeria.'},
    {'name': 'Ibibio', 'description': 'A Benue-Congo language spoken in southeastern Nigeria.'},
    {'name': 'Efik', 'description': 'A Benue-Congo language spoken in southeastern Nigeria.'},
    {'name': 'Gwari', 'description': 'A Niger-Congo language spoken in central Nigeria.'}
]

# Insert languages into the database
with app.app_context():
    for lang in languages:
        language = Language(name=lang['name'], description=lang['description'])
        db.session.add(language)
    db.session.commit()

print("Languages have been added to the database.")
