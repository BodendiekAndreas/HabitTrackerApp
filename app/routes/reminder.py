from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_login import login_required, current_user
from ..models import Reminder, Habit, db
from datetime import datetime

# Creating a blueprint for the reminder module.
reminder_bp = Blueprint('reminder', __name__, url_prefix='/reminders')


@reminder_bp.route('/')
@login_required
def index():
    # Route for displaying all reminders of the current user.
    # Redirects to the index page of the reminders.
    reminders = Reminder.query.join(Habit).filter(Habit.user_id == current_user.id).all()
    return render_template('reminder/index.html', reminders=reminders)


@reminder_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_reminder():
    # Route for adding a new reminder linked to a habit.
    # On successful POST operation, it redirects to the reminder index page.
    habits = Habit.query.filter_by(user_id=current_user.id).all()

    if request.method == 'POST':
        habit_id = request.form.get('habit_id')
        date_str = request.form.get('date')
        message = request.form.get('message')

        habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first()

        if not habit:
            flash('Invalid habit selected.', 'error')
        elif not date_str:
            flash('Please select a date.', 'error')
        else:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            new_reminder = Reminder(date=date_obj, message=message, habit_id=habit_id)
            db.session.add(new_reminder)
            db.session.commit()
            flash('New reminder added!')

        return redirect(url_for('reminder.index'))

    return render_template('reminder/add.html', habits=habits)


@reminder_bp.route('/edit/<int:reminder_id>', methods=['GET', 'POST'])
@login_required
def edit_reminder(reminder_id):
    # Route for editing an existing reminder.
    # Reminder id is passed as an argument.
    # Redirects to the index page of reminders after successful POST operation.
    reminder = Reminder.query.join(Habit).filter(
        Reminder.id == reminder_id,
        Habit.user_id == current_user.id
    ).first_or_404()

    if request.method == 'POST':
        # Convert the date from a string to a datetime.date
        reminder.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        reminder.message = request.form.get('message')
        db.session.commit()
        flash('Reminder updated successfully!')
        return redirect(url_for('reminder.index'))

    return render_template('reminder/edit.html', reminder=reminder)


@reminder_bp.route('/delete/<int:reminder_id>', methods=['POST'])
@login_required
def delete_reminder(reminder_id):
    # Route for deleting a reminder. Reminder id is passed as an argument.
    # Redirects to the reminder index page after successful deletion.

    reminder = Reminder.query.join(Habit).filter(
        Reminder.id == reminder_id,
        Habit.user_id == current_user.id
    ).first_or_404()

    db.session.delete(reminder)
    db.session.commit()
    flash('Reminder deleted successfully!')
    return redirect(url_for('reminder.index'))
