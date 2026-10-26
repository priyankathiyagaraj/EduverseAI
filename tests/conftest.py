import pytest
from app import create_app, db
from app.models.user import User
from app.models.college import College
from app.models.course import Course
from app.models.facility import Facility
from seed.seed_data import seed_database


@pytest.fixture(scope='function')
def app():
    """Creates a clean test application instance with in-memory SQLite database."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        # Seed test data
        seed_database()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Test client for HTTP requests."""
    return app.test_client()


@pytest.fixture(scope='function')
def admin_client(app, client):
    """Test client authenticated with administrator privileges."""
    with app.app_context():
        admin = User.query.filter_by(role='admin').first()
        with client.session_transaction() as sess:
            sess['user'] = admin.to_dict()
    return client


@pytest.fixture(scope='function')
def student_client(app, client):
    """Test client authenticated with standard student privileges."""
    with app.app_context():
        student = User.query.filter_by(role='student').first()
        with client.session_transaction() as sess:
            sess['user'] = student.to_dict()
    return client
