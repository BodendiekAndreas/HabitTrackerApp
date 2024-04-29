from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_user, logout_user, current_user

from .. import db
from ..models import User
from ..forms import LoginForm, RegistrationForm
from ..extensions import login_manager

# Creating a blueprint for the authentication module.
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@login_manager.user_loader
def load_user(user_id):
    # Function to load a user given a user_id.
    user = User.query.get(int(user_id))
    print("User Loader fetched user: {}".format(user))
    return user


def is_safe_url(target):
    # Check if a url is safe (internal link) for redirection.
    if target:
        if target.startswith('/'):
            return True
    return False


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Route for user login. If the user is already authenticated, it redirects to the main index.
    # It validates the submitted login form to ensure that the data is correct and logs in the user.
    if current_user.is_authenticated:
        current_app.logger.info("User already authenticated, redirecting to main index.")
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        print("User after query: {}".format(user))

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            current_app.logger.info("Login successful, redirecting.")
            print('The current user is: {}'.format(current_user))

            next_page = request.args.get('next')
            if next_page and not is_safe_url(next_page):
                return abort(400)
            return redirect(next_page or url_for('main.index'))

        else:
            flash('Invalid username or password')
            current_app.logger.info("Login failed.")

    return render_template('login.html', title='Login', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    #  Route for user registration. It validates the submitted registration form to ensure that the
    #  data is correct and registers the user by storing their data in the database.
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()  # Let the exception propagate.

        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('auth.login'))
    else:
        print("Form validation errors: {}".format(form.errors))

    return render_template('register.html', title='Register', form=form)


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))
