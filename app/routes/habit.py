from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from ..models import Habit, db, Completion
from ..forms import CustomHabitForm, PredefinedHabitForm
from .calendar import generate_calendar
from logging import getLogger
from datetime import date, timedelta

logger = getLogger(__name__)

DEFAULT_HABITS = [
    ('Morning Stretching', 'daily', 'Spend 10-15 minutes each morning doing a set of simple stretches.'),
    ('Digital Detox', 'weekly', 'Spend an entire day without any digital devices.'),
    ('30 Minutes Walk', 'daily', 'Take a brisk walk for 30 minutes, ideally in the morning.'),
    ('Meet A Friend', 'weekly', 'Catch up with a friend in person, over a call, or online.'),
    ('30 Minutes Me Time', 'daily', 'Spend 30 minutes alone doing something you love.')
]

# Creating a blueprint for the habit module.
habit_bp = Blueprint('habit', __name__, url_prefix='/habits')


@habit_bp.route('/')
@login_required
def index():
    # Route for showing all habits of the currently logged-in user.
    # Offering an option to filter out habits which have been completed.
    show_completed = request.args.get('show_completed', 'True') == 'True'
    if show_completed:
        habits = Habit.query.filter_by(user_id=current_user.id).all()
    else:
        habits = Habit.query.filter_by(user_id=current_user.id, completed=False).all()

    if not habits:
        return redirect(url_for('habit.add_habit'))

    habits_data = []
    for habit in habits:
        completions_count = habit.completions.count()
        habits_data.append({
            'habit': habit,
            'completions_count': completions_count
        })

    custom_habit_form = CustomHabitForm()
    predefined_habit_form = PredefinedHabitForm()
    predefined_habit_form.predefined_habit_name.choices = [(habit[0], habit[0]) for habit in DEFAULT_HABITS]
    return render_template('habit/list.html', habits_data=habits_data, custom_habit_form=custom_habit_form,
                           predefined_habit_form=predefined_habit_form, default_habits=DEFAULT_HABITS,
                           show_completed=show_completed)


@habit_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_habit():
    # Route for adding a new habit to the user's list. Provides two options: add a custom habit manually,
    # or select from a list of predefined habits.
    custom_habit_form = CustomHabitForm(request.form)
    predefined_habit_form = PredefinedHabitForm(request.form)
    predefined_habit_form.predefined_habit_name.choices = [(habit[0], habit[0]) for habit in DEFAULT_HABITS]

    if request.method == 'POST':
        if custom_habit_form.validate_on_submit():
            new_habit = Habit(name=custom_habit_form.name.data, description=custom_habit_form.description.data,
                              periodicity=custom_habit_form.periodicity.data, user_id=current_user.id)
            db.session.add(new_habit)
            db.session.commit()
            flash('New custom habit added!')
            return redirect(url_for('habit.index'))

        elif predefined_habit_form.validate_on_submit():
            selected_habit = next(
                habit for habit in DEFAULT_HABITS if habit[0] == predefined_habit_form.predefined_habit_name.data)
            name, periodicity, description = selected_habit
            new_habit = Habit(name=name, description=description, periodicity=periodicity,
                              user_id=current_user.id)
            db.session.add(new_habit)
            db.session.commit()
            flash('New predefined habit added!')
            return redirect(url_for('habit.index'))

    return render_template('habit/add.html', custom_habit_form=custom_habit_form,
                           predefined_habit_form=predefined_habit_form, DEFAULT_HABITS=DEFAULT_HABITS)


@habit_bp.route('/edit/<int:habit_id>', methods=['GET', 'POST'])
@login_required
def edit_habit(habit_id):
    # Route for editing an existing habit.
    habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first_or_404()
    form = CustomHabitForm(obj=habit)
    if form.validate_on_submit():
        form.populate_obj(habit)
        db.session.commit()
        flash('Habit updated!')
    return render_template('habit/edit.html', habit=habit, form=form)


@habit_bp.route('/delete/<int:habit_id>', methods=['POST'])
@login_required
def delete_habit(habit_id):
    # Route for deleting an existing habit.
    habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first_or_404()
    db.session.delete(habit)
    db.session.commit()
    flash('Habit deleted!')
    return redirect(url_for('habit.index'))


@habit_bp.route('/complete/<int:habit_id>', methods=['POST'])
@login_required
def mark_completed(habit_id):
    # Route for marking an existing habit as completed.
    # Generates a timestamp to mark the completion time.
    habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first_or_404()
    completion = Completion(completed_at=date.today(), habit_id=habit.id)
    db.session.add(completion)
    try:
        db.session.commit()
        flash('Habit marked as completed!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Error marking habit as completed! Details: {}'.format(str(e)), 'error')
    return redirect(url_for('habit.index'))


@habit_bp.route('/<int:habit_id>/calendar', methods=['POST', 'GET'])
@login_required
def habit_calendar(habit_id):
    habit = Habit.query.get_or_404(habit_id)

    # Get the current date.
    today = date.today()

    # Get the year and month from the URL arguments, if they exist.
    year = int(request.args.get('year', default=today.year))
    month = int(request.args.get('month', default=today.month))

    # Generate calendar data for the selected month and year.
    days, len_days = generate_calendar(year, month, habit_id)

    # Calculate the length.
    days_length = len(days)

    # Calculate dates for previous and next months.
    prev_month = date(year, month, 1) - timedelta(days=1)
    next_month = date(year, month, 1) + timedelta(days=32)
    next_month = date(next_month.year, next_month.month, 1)

    # Render the calendar template with the habit, days, len_days, days_length, and current month information.
    return render_template(
        'habit/calendar.html',
        habit=habit,
        days=days,
        len_days=len_days,
        days_length=days_length,
        current_month=date(year, month, 1).strftime('%B %Y'),
        year=year,
        month=month,
        today=today,
        prev_month=prev_month,
        next_month=next_month,
    )
