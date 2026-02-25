from datetime import datetime, date
import pytz

def calc_score(duration_sec: int) -> int:
    if duration_sec < 20:
        return 0
    if duration_sec < 45:
        return 1
    if duration_sec < 90:
        return 2
    return 3

def now_tz(tz_name: str) -> datetime:
    tz = pytz.timezone(tz_name)
    return datetime.now(tz)

def day_index(start_date: date, today: date) -> int:
    return (today - start_date).days + 1
