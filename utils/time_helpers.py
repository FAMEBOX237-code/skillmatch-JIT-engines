from datetime import datetime

def time_since(created_at):
    """
    Converts a datetime into 'x time ago'
    """

    # Gets current time
    now = datetime.now()

    # Ensure created_at is datetime (MySQL returns datetime already)
    diff = now - created_at


    # Convert everything to seconds
    seconds = diff.total_seconds()

    if seconds < 60:
        return f"{int(seconds)} seconds ago"

    minutes = seconds / 60
    if minutes < 60:
        return f"{int(minutes)} minutes ago"

    hours = minutes / 60
    if hours < 24:
        return f"{int(hours)} hours ago"

    days = hours / 24
    if days < 7:
        return f"{int(days)} days ago"

    weeks = days / 7
    return f"{int(weeks)} weeks ago"

    months = weeks / 4
    return f"{int(months)} months ago"

    years = months / 12
    return f"{int(years)} years ago"
