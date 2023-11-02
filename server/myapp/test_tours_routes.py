import pytest
from myapp import app, db  # Import your Flask app and database
from myapp.models import Story, Tours

# Set up a test client for your Flask app
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client


def test_get_nonexistent_story(client):
    response = client.get('/stories/999')
    assert response.status_code == 404


def test_get_nonexistent_tour(client):
    response = client.get('/tours/999')
    assert response.status_code == 404



# Clean up the test database after all tests are done
def teardown_module(module):
    with app.app_context():
        db.drop_all()

if __name__ == '__main__':
    pytest.main()
