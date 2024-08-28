import sys
import os

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Language

# Create the app and the database
app = create_app()
app.app_context().push()

# Delete all entries in the Language table
with app.app_context():
    db.session.query(Language).delete()
    db.session.commit()

print("All languages have been deleted from the database.")
