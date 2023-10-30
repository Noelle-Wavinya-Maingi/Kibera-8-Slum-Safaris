from . import db, bcrypt, mail
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Float,
    Date,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import validates, relationship
from datetime import datetime, timedelta
from flask_mail import Message
import secrets
import string


# Define the User model
class User(db.Model):
    __tablename__ = "users"

    # Define columns for the User Table
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(60), nullable=False)
    role = Column(String(20), nullable=False)

    # Constructor to initialize a new user
    def __init__(self, username, email, password, role):
        self.username = username
        self.email = email
        self.password = self.generate_password_hash(password)
        self.role = role

    # Method to generate a password hash
    def generate_password_hash(self, password):
        return bcrypt.generate_password_hash(password).decode("utf-8")

    # Method to check if the provided password matches the stored hash
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    # Validation method for the email field
    @validates("email")
    def validate_email(self, key, email):
        if not email:
            raise ValueError("Email is required")
        return email

    def __repr__(self):
        return f"User(id = {self.id}, username = {self.username}, email = {self.email}, role = {self.role})"


class Organization(db.Model):
    __tablename__ = "organizations"

    # Define columns for the table
    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True, nullable=False)
    description = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    status = Column(Boolean, default=False)
    password = Column(String(60))
    timestamp = Column(DateTime, default=datetime.utcnow)

    beneficiaries = relationship(
        "Beneficiary",
        secondary="beneficiaries_organizations",
        back_populates="organizations",
    )

    @validates("email")
    def validate_email(self, key, email):
        if not email:
            raise ValueError("Email is required")
        return email

    def approve_request(self):
        if not self.status:
            self.status = True
            temp_password = self.generate_temp_password()
            self.password = bcrypt.generate_password_hash(temp_password).decode("utf-8")
            self.send_password_email(temp_password)
            db.session.commit()
            return True
        return False

    def reject_request(self, reason):
        if not self.status:
            self.status = False
            self.send_rejection_email(reason)
            db.session.commit()
            return True
        return False

    def generate_temp_password(self):
        password_characters = string.ascii_letters + string.digits
        temp_password = "".join(secrets.choice(password_characters) for _ in range(6))
        return temp_password

    def send_password_email(self, temp_password):
        msg = Message(
            "Organization Registration Approved",
            sender="admin@gmail.com",
            recipients=[self.email],
        )
        msg.body = f"Your organization registration has been approved. Here is your login temporary password: {temp_password}"
        mail.send(msg)

    def send_rejection_email(self, reason):
        msg = Message(
            "Organization Registration Rejected",
            sender="admin@gmail.com",
            recipients=[self.email],
        )
        msg.body = f"Your organization has been rejected. Reason: {reason}"
        mail.send(msg)

    # Constructor to initialize a new organization
    def __init__(self, name, description, email):
        self.name = name
        self.description = description
        self.email = email

    def __repr__(self):
        return f"Organization(id={self.id}, name={self.name}, description={self.description}, status={self.status})"


class Donation(db.Model):
    __tablename__ = "donations"

    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    donor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    is_anonymous = Column(Boolean, default=False)
    recurrence_interval = Column(String(20))
    next_recurrence_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)

    donor = relationship("User", back_populates="donations")
    organization = relationship("Organization", back_populates="donations")

    def __init__(
        self, amount, donor_id, organization_id, is_anonymous, recurrence_interval=None
    ):
        self.amount = amount
        self.donor_id = donor_id
        self.organization_id = organization_id
        self.is_anonymous = is_anonymous
        self.recurrence_interval = recurrence_interval
        self.next_recurrence_date = self.calculate_next_recurrence_date()

    def calculate_next_recurrence_date(self):
        if self.recurrence_interval == "monthly":
            return datetime.utcnow() + timedelta(days=30)
        elif self.recurrence_interval == "annually":
            return datetime.utcnow() + timedelta(days=365)
        else:
            return None

    def process_recurring_donations(self):
        current_date = datetime.utcnow()
        if self.next_recurrence_date and current_date >= self.next_recurrence_date:
            # Create a new donation entry for the next recurrence
            new_donation = Donation(
                amount=self.amount,
                donor_id=self.donor_id,
                organization_id=self.organization_id,
                is_anonymous=self.is_anonymous,
                recurrence_interval=self.recurrence_interval,
            )
            self.next_recurrence_date = new_donation.calculate_next_recurrence_date()
            db.session.add(new_donation)
            db.session.commit()

    def send_notification(self, message):
        msg = Message(
            "Donation Notification",
            sender="admin@gmail.com",
            recipients=[self.donor.email],
        )
        msg.body = message
        mail.send(msg)


class Beneficiary(db.Model):
    __tablename__ = "beneficiaries"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer)
    gender = Column(String(10))
    address = Column(String(255))

    organizations = relationship(
        "Organization",
        secondary="beneficiaries_organizations",
        back_populates="beneficiaries",
    )

    def __init__(self, name, age=None, gender=None, address=None):
        self.name = name
        self.age = age
        self.gender = gender
        self.address = address

    def __repr__(self):
        return f"Beneficiary(id={self.id}, name={self.name}, age={self.age}, gender={self.gender}, address={self.address})"


beneficiaries_organizations = db.Table(
    "beneficiaries_organizations",
    Column("beneficiary_id", Integer, ForeignKey("beneficiaries.id")),
    Column("organization_id", Integer, ForeignKey("organizations.id")),
)


class Story(db.Model):
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)

    organization = db.relationship("Organization", back_populates="stories")

    def __init__(self, title, content, published_at, organization_id):
        self.title = title
        self.content = content
        self.published_at = published_at
        self.organization_id = organization_id

    def __repr__(self):
        return (
            f"Story(id={self.id}, title={self.title}, published_at={self.published_at})"
        )


class Inventory(db.Model):
    __tablename__ = "inventories"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    beneficiary_id = Column(Integer, ForeignKey("beneficiaries.id"), nullable=False)

    beneficiary = relationship("Beneficiary", back_populates="inventory")

    @validates("name")
    def validate_name(self, key, name):
        if not name:
            raise ValueError("Name is required")
        return name

    def __init__(self, name, quantity, beneficiary_id):
        self.name = name
        self.quantity = quantity
        self.beneficiary_id = beneficiary_id

    def __repr__(self):
        return f"Inventory(id={self.id}, name={self.name}, quantity={self.quantity}, beneficiary_id={self.beneficiary_id})"
    
class Tours(db.Model):
    __tablename__ = 'tours'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    image = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="tours")

    def __init__(self, name, price, user_id):
        self.name = name
        self.price = price
        self.user_id = user_id

    def __repr__(self):
        return f"Tours(id={self.id}, name={self.name}, price={self.price}, date={self.date})"

