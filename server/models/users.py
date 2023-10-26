from . import db, bcrypt
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import validates


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
    @validates("email")
    def validate_email(self, key, email):
        if not email:
            raise ValueError("Email is required")
        return email

    def __repr__(self):
        return f"User(id = {self.id}, username = {self.username}, email = {self.email}, role = {self.role})"
