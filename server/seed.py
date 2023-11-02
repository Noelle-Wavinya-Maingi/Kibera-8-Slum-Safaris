from myapp import app, db, bcrypt, mail
from myapp.models import User, Organization, Donation, Beneficiary, Story, Inventory, Tours, user_tours, beneficiaries_organizations
import secrets
import string
from datetime import datetime

def seed_database():
    print("Seeding Database....")
    with app.app_context():
        # Delete existing data
        db.session.query(User).delete()
        db.session.query(Organization).delete()
        db.session.query(Donation).delete()
        db.session.query(Beneficiary).delete()
        db.session.query(Story).delete()
        db.session.query(Inventory).delete()
        db.session.query(Tours).delete()
        db.session.query(user_tours).delete()
        db.session.query(beneficiaries_organizations).delete()


        # Create a sample user
        user1 = User(
            username="sample_user",
            email="user@example.com",
            password="sample_password",
            role="Admin",
        )

        db.session.add(user1)
        db.session.commit()
         
        print("User Seeded!!")
        # Create a sample organization
        organization1 = Organization(
            name="Sample Organization",
            description="Description of the sample organization",
            email="org@example.com",
        )

        db.session.add(organization1)
        db.session.commit()

        print("Organization Seeded!!")
        # Create a sample donation
        donation1 = Donation(
            amount=100.0,
            donor_id=user1.id,
            organization_id=organization1.id,
            is_anonymous=False,
        )

        db.session.add(donation1)
        db.session.commit()

        print("Donation Seeded!!")

        # Create a sample beneficiary
        beneficiary1 = Beneficiary(
            name="Sample Beneficiary",
            age=30,
            gender="Male",
            address="123 Sample Street",
        )

        db.session.add(beneficiary1)
        db.session.commit()

        # Create a sample story
        story1 = Story(
            title="Sample Story",
            content="This is a sample story content.",
            created_at=datetime.utcnow(),
            organization_id=organization1.id,
            image="https://www.google.com/imgres?imgurl=https%3A%2F%2Fmedia.tacdn.com%2Fmedia%2Fattractions-splice-spp-674x446%2F07%2Fc1%2F97%2F0e.jpg&tbnid=gP8VHqXNdoNHrM&vet=12ahUKEwiigreb5p2CAxUdlCcCHacXAjwQMygBegQIARA6..i&imgrefurl=https%3A%2F%2Fwww.viator.com%2Ftours%2FNairobi%2FKibera-Slum-Guided-Day-Tour-from-Nairobi%2Fd5280-21143P25&docid=P2vEY0r2DFC8rM&w=669&h=446&q=kibera%20tourist%20spot&ved=2ahUKEwiigreb5p2CAxUdlCcCHacXAjwQMygBegQIARA6",
        )

        db.session.add(story1)
        db.session.commit()

        print("Story Seeded!!")
        # Create a sample inventory item
        inventory1 = Inventory(
            name="Sample Item",
            quantity=10,
            user_id=user1.id,
        )

        db.session.add(inventory1)
        db.session.commit()
        print("inventory seeded")

        # Create a sample tour
        tour1 = Tours(
            name="Sample Tour",
            image="https://www.google.com/imgres?imgurl=https%3A%2F%2Fmedia.tacdn.com%2Fmedia%2Fattractions-splice-spp-674x446%2F07%2Fc1%2F97%2F0e.jpg&tbnid=gP8VHqXNdoNHrM&vet=12ahUKEwiigreb5p2CAxUdlCcCHacXAjwQMygBegQIARA6..i&imgrefurl=https%3A%2F%2Fwww.viator.com%2Ftours%2FNairobi%2FKibera-Slum-Guided-Day-Tour-from-Nairobi%2Fd5280-21143P25&docid=P2vEY0r2DFC8rM&w=669&h=446&q=kibera%20tourist%20spot&ved=2ahUKEwiigreb5p2CAxUdlCcCHacXAjwQMygBegQIARA6",
            price=100.0,
        )

        db.session.add(tour1)
        db.session.commit()
        print("Tours seeded")


       # Create entries in the user_tours association table
        user_tours_entry = user_tours.insert().values(
            user_id=user1.id,
            tours_id=tour1.id,
            tour_date=datetime.utcnow(),
        )

        db.session.execute(user_tours_entry)
        db.session.commit()


        # Create entries in the beneficiaries_organizations association table
        beneficiaries_organizations_entry = beneficiaries_organizations.insert().values(
            beneficiary_id=beneficiary1.id,
            organization_id=organization1.id
        )
        db.session.execute(beneficiaries_organizations_entry)
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    seed_database()
    print("Database seeded succeeded!!")