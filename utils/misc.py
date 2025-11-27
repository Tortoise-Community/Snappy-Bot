import datetime

def format_timedelta(time_delta: datetime.timedelta) -> str:
    total_seconds = int(time_delta.total_seconds())
    days, remainder = divmod(total_seconds, 60 * 60 * 24)
    hours, remainder = divmod(remainder, 60 * 60)
    minutes, seconds = divmod(remainder, 60)
    return f"{days}d {hours}h {minutes}m and {seconds}s"