import pytest
from flask import url_for
from app import create_app, db
from app.models import User, Habit, Completion
from faker import Faker
from app.routes.analytics import AnalyticsService
from datetime import datetime, timedelta


# Fixture to setup and tear down application context per function.
@pytest.fixture(scope='function')
def test_app():
    # Test application instance and setup database.
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        session = db.session
        yield app, session
        session.close()
        db.drop_all()


# Fixture to return an instance of test client per function.
@pytest.fixture(scope='function')
def test_client(test_app):
    app, _ = test_app
    return app.test_client()


# Helper function to create a new user.
def create_user(username, email, password, session):
    user = User(username=username, email=email)
    user.set_password(password)
    print('User before commit', user, user.id)  # This will likely print 'None' for user.id
    session.add(user)
    session.commit()
    print('User after commit', user, user.id)  # If successful, this should print an integer id
    return user


# Fixture to create a test user and log him in with the test client.
@pytest.fixture(scope='function')
def user_with_login(test_client, test_app):
    _, session = test_app
    fake = Faker()
    fake_email = fake.email()
    fake_username = fake.user_name()
    password = 'testpassword123'
    user = create_user(fake_username, fake_email, password, session)
    session.commit()  # Ensure user is committed to the DB
    with test_client:
        result = test_client.post(url_for('auth.login'), data={'email': fake_email, 'password': password},
                                  follow_redirects=True)
        assert 200 == result.status_code
    yield user


def create_habit(name, description, periodicity, user_id, session):
    habit = Habit(name=name, description=description, periodicity=periodicity, user_id=user_id)
    session.add(habit)
    session.commit()


# Fixture to create habits for test user with their description and periodicity.
@pytest.fixture(scope='function')
def habits_created(test_client, user_with_login, test_app):
    user = user_with_login
    app, session = test_app
    with app.app_context():
        for _ in range(3):
            create_habit(Faker().sentence(), Faker().sentence(), 'daily', user.id, session)


# Helper function to mark a habit completed.
def mark_habit_completed(habit_id, completed_at):
    completion = Completion(habit_id=habit_id, completed_at=completed_at)
    db.session.add(completion)
    db.session.commit()


# Test case for get_habits method.
def test_get_habits(test_client, test_app, user_with_login):
    app, session = test_app
    with app.app_context():
        habits = AnalyticsService.get_habits(user_with_login.id)
        assert len(habits) == 0

        user = user_with_login
        create_habit("Test Habit", "Test Description", "daily", user.id, session)
        habits = AnalyticsService.get_habits(user_with_login.id)
        assert len(habits) == 1


# Test case for get_habits_by_periodicity method.
def test_get_habits_by_periodicity(test_client, test_app, user_with_login, habits_created):
    app, session = test_app
    with app.app_context():
        user = user_with_login
        create_habit("Test Weekly Habit", "Test Weekly Description", "weekly", user.id, session)

        habits = AnalyticsService.get_habits_by_periodicity("daily", user_with_login.id)
        assert len(habits) == 3


# Test case for calculate_longest_streak method.
def test_calculate_longest_streak(test_client, test_app, user_with_login, habits_created):
    app, session = test_app
    with app.app_context():
        user = user_with_login
        habit_test = Habit.query.filter_by(user_id=user.id).first()

        streak = AnalyticsService.calculate_longest_streak(habit_test.id)
        assert streak == 0

        for i in range(5):
            mark_habit_completed(habit_test.id, datetime.now() - timedelta(days=i))

        streak = AnalyticsService.calculate_longest_streak(habit_test.id)
        assert streak == 5


# Test case for longest_streak_for_a_given_habit method.
def test_longest_streak_for_a_given_habit(test_client, test_app, user_with_login, habits_created):
    app, session = test_app
    with app.app_context():
        user = user_with_login
        habit_test = Habit.query.filter_by(user_id=user.id).first()
        url = url_for('analytics.longest_streak_for_a_given_habit', habit_id=habit_test.id)

        response = test_client.get(url, follow_redirects=True)
        assert response.status_code == 200

        longest_streak = AnalyticsService.calculate_longest_streak(habit_test.id)
        assert str(longest_streak) in response.data.decode('utf-8')

        for i in range(5):
            mark_habit_completed(habit_test.id, datetime.now() - timedelta(days=i))

        response = test_client.get(url, follow_redirects=True)
        assert response.status_code == 200

        longest_streak = AnalyticsService.calculate_longest_streak(habit_test.id)
        assert str(longest_streak) in response.data.decode('utf-8')
