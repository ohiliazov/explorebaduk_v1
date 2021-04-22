def seconds_to_str(seconds: int) -> str:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)

    time_str = ""
    if weeks:
        time_str += f"{weeks}w"
    if days:
        time_str += f" {days}d"
    if hours:
        time_str += f" {hours}h"
    if minutes:
        time_str += f" {minutes}m"
    if seconds:
        time_str += f" {seconds}s"

    return time_str
