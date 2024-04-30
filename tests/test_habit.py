import pytest
from flask import url_for
from app import create_app, db
from app.models import User, Habit, Completion
from faker import Faker


# Fixture to setup and tear down application context per function.
@pytest.fixture(scope='function')
def test_app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()  # Ensure all tables are created.
        yield app  # this will be where the testing happens.
        db.drop_all()  # Drop database tables after tests.


# Function to create a new user.
def create_user(username, email, password):
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()


# Fixture to return an instance of test client per function.
@pytest.fixture(scope='function')
def test_client(test_app):
    return test_app.test_client()


# Fixture to create a test user and log him in with the test client.
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


# Fixture to create a new habit for test user.
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


# Test case for adding a habit.
def test_add_habit(test_client, user_with_login, test_app):
    response = test_client.post(url_for('habit.add_habit'), data={
        'name': 'Read a Book',
        'description': 'Read one chapter of a book',
        'periodicity': 'daily'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'New custom habit added!' in response.get_data(as_text=True)
    with test_app.app_context():
        user = User.query.filter_by(email=user_with_login[1]).first()
        count = Habit.query.filter_by(user_id=user.id).count()
        assert count == 1


# Test case for editing a habit.
def test_edit_habit(test_client, test_app, habit_created):
    habit_id = habit_created.id
    response = test_client.post(url_for('habit.edit_habit', habit_id=habit_id), data={
        'name': 'Read Two Books',
        'description': 'Read two chapters of a book',
        'periodicity': 'daily'
    }, follow_redirects=True)

    assert response.status_code == 200

    # Query the database to verify that the habit's details got updated
    with test_app.app_context():
        habit = Habit.query.get(habit_id)
        assert habit.name == 'Read Two Books'
        assert habit.description == 'Read two chapters of a book'
        assert habit.periodicity == 'daily'

    # Check whether the response data contains 'Habit Updated!' or some other message by exploring logged page content
    page_content = response.get_data(as_text=True)
    print(page_content)


# Test case for deleting a habit.
def test_delete_habit(test_client, test_app, habit_created):
    habit_id = habit_created.id
    response = test_client.post(url_for('habit.delete_habit', habit_id=habit_id), follow_redirects=True)
    assert response.status_code == 200
    assert 'Habit deleted!' in response.get_data(as_text=True)


# Test case for marking a habit as completed.
def test_mark_completed(test_client, test_app, habit_created):
    habit_id = habit_created.id
    response = test_client.post(url_for('habit.mark_completed', habit_id=habit_id), follow_redirects=True)
    assert response.status_code == 200
    assert 'Habit marked as completed!' in response.get_data(as_text=True)
    with test_app.app_context():
        completion_count = Completion.query.filter_by(habit_id=habit_id).count()
        assert completion_count == 1


# This fixture will add 28 completions to a habit
@pytest.fixture(scope='function')
def habit_with_completions(test_app, habit_created):
    from datetime import timedelta, date

    # with each iteration, a date in the past 28 days is set as completion date for a habit
    for i in range(1, 29):
        completion_date = date.today() - timedelta(days=i)
        completion = Completion(completed_at=completion_date, habit_id=habit_created.id)
        db.session.add(completion)

    db.session.commit()

    return habit_created


# Then, a new test case to test habit completions
def test_habit_completions(test_client, test_app, habit_with_completions):
    habit_id = habit_with_completions.id
    with test_app.app_context():
        completion_count = Completion.query.filter_by(habit_id=habit_id).count()
        assert completion_count == 28  # assert that 28 completions have been created

