from datetime import datetime, timedelta
from ..models import Completion
from typing import List, Tuple, Optional
from .. import db


def generate_calendar(year: int, month: int, habit_id: int) -> Tuple[List[Tuple[int, int, Optional[bool]]], int]:
    # Create the start date of the month
    start_date = datetime(year, month, 1)
    # Compute the last date of the month in a more straightforward way
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)

    days = []
    # Generate each day of the month
    for single_date in (start_date + timedelta(n) for n in range((end_date - start_date).days + 1)):
        # Check if there's a completion record for this date
        completed = Completion.query.filter((Completion.habit_id == habit_id) & (
                db.func.date(Completion.completed_at) == single_date.date())).first() is not None

        days.append((single_date.day, single_date.weekday(), completed))

    len_days = len(days)
    return days, len_days
