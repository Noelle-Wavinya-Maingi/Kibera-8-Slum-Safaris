import pytest
from flask import json
from myapp import app, db
from myapp.models import User


# Define a fixture to initialize the Flask app and database for testing
@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


def create_test_user(email, password, username, role):
    # Helper function to create a user in the test database
    user = User(email=email, password=password, username=username, role=role)
    with app.app_context():
        db.session.add(user)
        db.session.commit()


def test_user_login_invalid_credentials(client):
    # Create a test user in the test database
    create_test_user("test@example.com", "testpassword", "testusername", "donor")

    # Define login data with invalid password
    login_data = {
        "email": "test@example.com",
        "password": "wrongpassword",
    }

    response = client.post("/user/login", json=login_data)
    assert response.status_code == 404


def test_user_login_nonexistent_user(client):
    # Define login data for a user that does not exist in the test database
    login_data = {
        "email": "nonexistent@example.com",
        "password": "password",
    }

    response = client.post("/user/login", json=login_data)
    assert response.status_code == 404
