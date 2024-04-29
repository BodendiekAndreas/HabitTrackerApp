from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from flask_wtf import FlaskForm
from .models import User


class LoginForm(FlaskForm):
    # Form class for handling user login.
    # Includes the user's email, password, an option to be remembered
    # by the application, and a submit button.
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    # Form class for handling user registration.
    # Includes the user's username, email, password, password confirmation, and a submit button.
    # Also includes validation checks for unique usernames and emails.
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        # Custom username validation function.
        # Checks whether the username is already taken. If it is, throws a validation error.
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        # Custom email validation function.
        # Checks whether the email is already taken. If it is, throws a validation error.
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class CustomHabitForm(FlaskForm):
    # Form class for adding custom habits.
    # Includes the habit's name, description, periodicity, and a submit button.
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    periodicity = SelectField('Periodicity', choices=[('daily', 'Daily'), ('weekly', 'Weekly')],
                              validators=[DataRequired()])
    submit = SubmitField('Add Custom Habit')


class PredefinedHabitForm(FlaskForm):
    # Form class for adding predefined habits.
    # Includes a selection field for predefined habit names, and a submit button.
    predefined_habit_name = SelectField('Predefined Habit Name',
                                        choices=[('choice1', 'Choice 1'), ('choice2', 'Choice 2')],
                                        validators=[DataRequired()])
    submit = SubmitField('Add Predefined Habit')


class SelectHabitForm(FlaskForm):
    # Form class for selecting a habit from a list.
    # Includes a selection field for habit_ids.
    habit_id = SelectField('Select Habit', coerce=int, validators=[DataRequired()])


class FilterPeriodicityForm(FlaskForm):
    # Form class for filtering habits by periodicity.
    # Includes a selection field for periodicity options.
    periodicity = SelectField('Select Periodicity', choices=[('daily', 'Daily'), ('weekly', 'Weekly')],
                              validators=[DataRequired()])
