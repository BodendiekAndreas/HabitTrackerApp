import pytest
from flask import url_for
from sqlalchemy import create_engine
from app import create_app, db
from app.models import User
from sqlalchemy.exc import IntegrityError
from faker import Faker

fake = Faker()

# create the app for test context.
app = create_app('default')
app.config['SERVER_NAME'] = 'localhost:5000'


# fixture for session-wide SQLAlchemy Engine.
@pytest.fixture(scope='session')
def engine():
    return create_engine('Your DB Connection String/URI')


# fixture for session-wide database connection.
@pytest.fixture(scope='session')
def connection(engine):
    with engine.connect() as connection:
        yield connection


# fixture for function-scoped SQLAlchemy Session.
@pytest.fixture(scope='function')
def db_session(connection):
    transaction = connection.begin()
    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options)

    db.session = session

    yield session

    transaction.rollback()
    session.remove()


# fixture for module-scoped application.
@pytest.fixture(scope='module')
def test_app():
    _app = create_app('testing')
    _app.config['SERVER_NAME'] = 'localhost:5000'
    with _app.app_context():
        db.create_all()
        yield _app
        db.session.remove()
        db.drop_all()


# fixture for module-scoped test client.
@pytest.fixture(scope='module')
def test_client(test_app):
    return test_app.test_client()


# fixture for function-scoped database initialization.
@pytest.fixture(scope='function')
def init_database(test_app):
    with test_app.app_context():
        db.create_all()

        yield

        db.session.remove()
        db.drop_all()


# fixture for logged in client.
@pytest.fixture
def logged_in_client(test_client, init_database):
    with test_client:
        test_client.post(url_for('auth.login'), data={
            'email': 'user@example.com',
            'password': 'password2'
        }, follow_redirects=True)
        yield test_client


# function to add a new user to the database.
def insert_user(email, username):
    new_user = User(email=email, username=username)
    try:
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return "User with this email already exists."
