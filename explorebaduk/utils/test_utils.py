import random


def generate_time_settings(time_system: str, **kwargs):
    time_settings = {
        "time_system": time_system,
        **kwargs,
    }

    if time_system == "unlimited":
        return time_settings

    time_settings.setdefault("main_time", random.randint(1, 3600))
    if time_system == "absolute":
        return time_settings

    if time_system == "fischer":
        time_settings.setdefault("bonus", random.randint(1, 10))
        return time_settings

    time_settings.setdefault("overtime", random.randint(1, 60))
    if time_system == "byoyomi":
        time_settings.setdefault("stones", 1)
    elif time_system == "canadian":
        time_settings.setdefault("periods", 1)

    return time_settings
