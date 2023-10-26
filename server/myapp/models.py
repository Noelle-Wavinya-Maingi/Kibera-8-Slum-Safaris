from . import db, bcrypt, mail
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import validates
from datetime import datetime
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

    # Method to check if the provided password maches the stored hash
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    # Validation method for the email field
    @validates("email ")
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
        msg = Message("Organization Registration Approved", sender="admin@gmail.com", recipients=[self.email])
        msg.body = f"Your organization registration has been approved. Here is your login temporary password: {temp_password}"
        mail.send(msg)

    def send_rejection_email(self, reason):
        msg = Message('Organization Registration Rejected', sender='admin@gmail.com', recipients=[self.email])
        msg.body = f'Your organization has been rejected. Reason: {reason}'
        mail.send(msg)

    # Constructor to initialize a new organization
    def __init__(self, name, description, email):
        self.name = name
        self.description = description
        self.email = email

    def __repr__(self):
        return f"Organization(id={self.id}, name={self.name}, description={self.description}, status={self.status})"