from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required
from ..models import Habit, Completion
from itertools import groupby
from ..forms import FilterPeriodicityForm, SelectHabitForm
from flask_login import current_user
from sqlalchemy.orm import aliased
from .. import db

# creating blueprint for analytics module.
analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')


class AnalyticsService:
    # Service class for dealing with analytics related operations.
    @staticmethod
    def get_habits(user_id):
        # Retrieves the Habits for a particular user.
        return Habit.query.filter_by(user_id=user_id).all()

    @staticmethod
    def get_habits_by_periodicity(periodicity, user_id):
        # Retrieves the Habits for a particular user filtered by periodicity.
        return Habit.query.filter_by(periodicity=periodicity, user_id=user_id).all()

    @staticmethod
    def get_longest_streak_all_habits():
        # Calculates and retrieves the longest streak among all habits of current user.
        habit_streaks = {}
        longest_streak = 0
        habits = Habit.query.filter_by(user_id=current_user.id).all()

        for habit in habits:
            current_streak = AnalyticsService.calculate_longest_streak(habit.id)
            habit_streaks[habit] = current_streak
            if current_streak > longest_streak:
                longest_streak = current_streak

        habits_with_longest_streak = [habit for habit, streak in habit_streaks.items() if streak == longest_streak]

        return habits_with_longest_streak, longest_streak

    @staticmethod
    def calculate_longest_streak(habit_id):
        habit_alias = aliased(Habit)
        completions = db.session.query(Completion).join(
            habit_alias, habit_alias.id == Completion.habit_id
        ).filter(
            habit_alias.id == habit_id
        ).order_by(Completion.completed_at).all()

        if not completions:
            return 0
        dates = [completion.completed_at.date() for completion in completions]
        streaks = [len(list(group)) for _, group in groupby(enumerate(dates), lambda ix: ix[0] - ix[1].toordinal())]
        return max(streaks, default=0)


@analytics_bp.route('/')
@login_required
def index():
    # Index route for analytics module.
    # Shows overview of analytical functions.
    return render_template('analytics/index.html')


@analytics_bp.route('/all_habits')
@login_required
def all_habits():
    # Route to display the list of all habits for the current user.
    habits = AnalyticsService.get_habits(current_user.id)
    habits_details = [{
        'name': habit.name,
        'description': habit.description,
        'periodicity': habit.periodicity,
        'completions_count': get_completions_count(habit.id),
        'longest_streak': AnalyticsService.calculate_longest_streak(habit.id)
    } for habit in habits]

    return render_template('analytics/all_habits.html', all_habits_details=habits_details)


@analytics_bp.route('/habits_by_periodicity', methods=['GET', 'POST'])
@login_required
def habits_by_periodicity():
    # Route to filter habits by their periodicity. (daily or weekly)
    form = FilterPeriodicityForm()

    # This will handle the form submission and validate it
    if request.method == 'POST' and form.validate_on_submit():
        periodicity = form.periodicity.data
        user_id = current_user.id
        # Validate if the periodicity is one of the acceptable values
        if periodicity not in ['daily', 'weekly']:
            flash('Invalid periodicity selected', 'error')
            return redirect(url_for('analytics.index'))

        habits = AnalyticsService.get_habits_by_periodicity(periodicity, user_id)
        habits_details = [{
            'name': habit.name,
            'description': habit.description,
            'periodicity': habit.periodicity,
            'completions_count': get_completions_count(habit.id),
            'longest_streak': AnalyticsService.calculate_longest_streak(habit.id)
        } for habit in habits]

        return render_template('analytics/habits_by_periodicity.html',
                               habits_details=habits_details,
                               periodicity=periodicity,
                               form=form)

    # For GET requests or if form is not validated, just show the form
    return render_template('analytics/habits_by_periodicity.html', form=form)


def get_completions_count(habit_id):
    # Helper function to get the completion count for a specific habit.
    return Completion.query.filter_by(habit_id=habit_id).count()


@analytics_bp.route('/longest_streak_all_habits')
@login_required
def longest_streak_all_habits():
    # Route to display the habits with the longest completion streaks.
    habits, longest_streak = AnalyticsService.get_longest_streak_all_habits()
    return render_template('analytics/longest_streak_all_habits.html', habits=habits, longest_streak=longest_streak)


@analytics_bp.route('/longest_streak_for_a_given_habit/<int:habit_id>', methods=['GET', 'POST'])
@login_required
def longest_streak_for_a_given_habit(habit_id):
    # Route to calculate and display the longest streak for a specific habit.
    current_app.logger.info('Calculating longest streak for habit ID: {}'.format(habit_id))
    habit = Habit.query.get_or_404(habit_id)
    longest_streak = AnalyticsService.calculate_longest_streak(habit.id)
    current_app.logger.info('Calculated longest streak: {}'.format(longest_streak))

    form = SelectHabitForm()
    form.habit_id.choices = [(habit.id, habit.name) for habit in Habit.query.filter_by(user_id=current_user.id).all()]
    return render_template('analytics/longest_streak_for_habit.html', habit=habit,
                           longest_streak=longest_streak, form=form)


@analytics_bp.route('/filter_habits', methods=['GET', 'POST'])
@login_required
def filter_habits():
    # Route to filter habits by their periodicity.
    form = FilterPeriodicityForm()
    if form.validate_on_submit():
        periodicity = form.periodicity.data
        return redirect(url_for('analytics.habits_by_periodicity', periodicity=periodicity))
    return render_template('analytics/habits_by_periodicity.html', form=form)


@analytics_bp.route('/select_habit_for_streak', methods=['GET', 'POST'])
@login_required
def select_habit_for_streak():
    # Route to select a specific habit for viewing its longest streak.
    form = SelectHabitForm()
    form.habit_id.choices = [(habit.id, habit.name) for habit in Habit.query.filter_by(user_id=current_user.id).all()]
    if form.validate_on_submit():
        habit_id = form.habit_id.data
        return redirect(url_for('analytics.longest_streak_for_a_given_habit', habit_id=habit_id))
    return render_template('analytics/longest_streak_for_habit.html', form=form)
