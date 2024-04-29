import pytest
from flask import url_for
from app import create_app, db
from app.models import Reminder, User, Habit
from faker import Faker


# Fixture to set up and tear down application context per function.
@pytest.fixture(scope='function')
def test_app():
    app = create_app('testing')
    with app.app_context():
        db.create_all() # Ensure all tables are created.
        yield app # this will be where the testing happens.
        db.drop_all() # Drop database tables after tests.


# Function to create a new user.
def create_user(username, email, password):
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()


# Fixture to return an instance of the test client per function.
@pytest.fixture(scope='function')
def test_client(test_app):
    return test_app.test_client()


# Fixture to create a test user and log them in with the test client.
@pytest.fixture(scope='function')
def user_with_login(test_client):
    fake = Faker()
    fake_email = fake.email()
    fake_username = fake.user_name()
    password = 'testpassword123'
    create_user(fake_username, fake_email, password)

    result = test_client.post('/auth/login', data={'email': fake_email, 'password': password}, follow_redirects=True)
    assert 200 == result.status_code
    yield fake_username, fake_email


# Fixture to create a new habit for the test user.
@pytest.fixture(scope='function')
def habit_created(test_client, user_with_login, test_app):
    response = test_client.post(url_for('habit.add_habit'), data={
        'name': 'Read a Book',
        'description': 'Read one chapter of a book',
        'periodicity': 'daily'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert 'New custom habit added!' in response.get_data(as_text=True)

    with test_app.app_context():
        user = User.query.filter_by(email=user_with_login[1]).first()
        habit_created = Habit.query.filter_by(user_id=user.id).first()
        assert habit_created is not None
    return habit_created


# Fixture to create a new reminder for the test user.
@pytest.fixture(scope='function')
def reminder_created(test_client, user_with_login, test_app, habit_created):
    habit_id = habit_created.id
    response = test_client.post(url_for('reminder.add_reminder'), data={
        'habit_id': habit_id,
        'date': '2023-01-01',
        'message': 'TestReminder'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert 'New reminder added!' in response.get_data(as_text=True)

    with test_app.app_context():
        reminder_created = Reminder.query.filter_by(habit_id=habit_id).first()
        assert reminder_created is not None
    return reminder_created


# Test case for getting reminders index.
def test_reminders_index(test_client, user_with_login, reminder_created):
    response = test_client.get(url_for('reminder.index'))
    assert b'TestReminder' in response.data


# Test case for adding a reminder.
def test_add_reminder(test_client, user_with_login, habit_created):
    response = test_client.post(url_for('reminder.add_reminder'), data={
        'habit_id': habit_created.id,
        'date': '2023-01-01',
        'message': 'TestReminder'
    }, follow_redirects=True)

    assert b'TestReminder' in response.data


# Test case for editing a reminder.
def test_edit_reminder(test_client, user_with_login, reminder_created, test_app):
    reminder_id = reminder_created.id
    response = test_client.post(url_for('reminder.edit_reminder', reminder_id=reminder_id), data={
        'date': '2023-01-01',
        'message': 'UpdatedTestReminder'
    }, follow_redirects=True)

    assert response.status_code == 200

    with test_app.app_context():
        reminder = Reminder.query.get(reminder_id)
        assert reminder.date.strftime('%Y-%m-%d') == '2023-01-01'
        assert reminder.message == 'UpdatedTestReminder'

    assert b'UpdatedTestReminder' in response.data


# Test case for deleting a reminder.
def test_delete_reminder(test_client, user_with_login, reminder_created):
    reminder_id = reminder_created.id
    response = test_client.post(url_for('reminder.delete_reminder', reminder_id=reminder_id), follow_redirects=True)

    assert b'Reminder deleted successfully!' in response.data
