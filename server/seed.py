from myapp import app, db, bcrypt, mail
from myapp.models import User, Organization
import secrets
import string

def seed_database():
    print("Hey")
    with app.app_context():
        # Delete existing data (optional)
        db.session.query(User).delete()
        db.session.query(Organization).delete()

        # Create a sample user
        user1 = User(
            username="sample_user",
            email="user@example.com",
            password="sample_password",  
            role="Admin",  
        )

        # Create a sample organization
        organization1 = Organization(
            name="Sample Organization",
            description="Description of the sample organization",
            email="org@example.com",
        )

        # Add the user and organization to the database
        db.session.add(user1)
        db.session.add(organization1)
        db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    seed_database()
    print("Database seeded successfully.")
