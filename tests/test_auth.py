from app import create_app, db as _db
from app.models import User
from flask_login import current_user
from faker import Faker
import pytest


# Fixture for creating a Flask test client.
@pytest.fixture(scope='session')
def client():
    flask_app = create_app('testing')
    with flask_app.app_context():
        with flask_app.test_client() as testing_client:
            yield testing_client


# Fixture for setting up and tearing down the test database
@pytest.fixture(scope='session')
def init_database(client):
    # In the context of the test client, set up the tables in the database.
    with client.application.app_context():
        _db.create_all()  # Ensure all tables are created

        # Add a fake user to the database before running the tests
        fake = Faker()
        fake_username = fake.user_name()
        fake_email = fake.email()

        user = User(username=fake_username, email=fake_email)
        user.set_password("test")
        _db.session.add(user)
        _db.session.commit()

    yield  # this is where the testing happens.

    # After the test, close the session and drop all tables in the database.
    _db.session.close()
    _db.drop_all()


# Test case for /auth/register route.
def test_register(client, init_database):
    fake = Faker()
    fake_email = fake.email()
    fake_username = fake.user_name()

    response = client.post(
        '/auth/register',
        data={'username': fake_username, 'email': fake_email, 'password': 'a', 'password2': 'a'}
    )

    assert 302 == response.status_code
    assert User.query.filter_by(email=fake_email).first() is not None


# Test case for /auth/login route.
def test_login(client, init_database):
    # Generate a fake email and username
    fake = Faker()
    fake_email = fake.email()
    fake_username = fake.user_name()

    user = User(username=fake_username, email=fake_email)
    user.set_password("test")
    _db.session.add(user)
    _db.session.commit()

    response = client.post(
        '/auth/login',
        data={'email': fake_email, 'password': 'test'},
        follow_redirects=True
    )

    assert 200 == response.status_code
    assert current_user.is_authenticated
