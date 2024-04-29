from flask import Blueprint, render_template
from datetime import datetime
from ..models import Reminder
from sqlalchemy.orm import joinedload

# Define the Blueprint.
main_bp = Blueprint('main', __name__, url_prefix='')


@main_bp.route('/', methods=['GET'])
def index():
    current_date = datetime.now().date()  # Get the current date.

    # Query for reminders that are due today, and their corresponding habits.
    due_reminders = Reminder.query.options(joinedload(Reminder.habit)).filter_by(date=current_date).all()

    # Pass the reminders to the template.
    return render_template('index.html', reminders=due_reminders)
