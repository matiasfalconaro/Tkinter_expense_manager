import datetime


def get_current_month() -> int:
    """Returns the current month as an integer."""
    return datetime.datetime.now().month
