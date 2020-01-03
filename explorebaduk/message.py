import re
from typing import Tuple, Dict, Any


MESSAGE_PATTERNS = {
    "auth": [
        re.compile(r"^auth (?P<action>login) (?P<username>\w+) (?P<token>\w{64})$"),
        re.compile(r"^auth (?P<action>logout)$"),
    ],
    "challenge": [
        re.compile(
            r"challenge (?P<action>new) (?P<type>\d),(?P<rules>\d),(?P<players>\d+),"
            r"(?P<board_size>\d{,2}(?::\d{,2})?) "
            r"F(?P<open>\d)(?P<undo>\d)(?P<pause>\d) "
            r"T(?P<tyme_system>\d+),(?P<main_time>\d+),"
            r"(?P<overtime>\d+),(?P<periods>\d+),(?P<stones>\d+),"
            r"(?P<bonus>\d+),(?P<delay>\d+)"
        ),
        re.compile(r"challenge (?P<action>cancel) (?P<challenge_id>\d+)"),
        re.compile(r"challenge (?P<action>join) (?P<challenge_id>\d+)"),
        re.compile(r"challenge (?P<action>leave) (?P<challenge_id>\d+)"),
        re.compile(r"challenge (?P<action>accept) (?P<challenge_id>\d+) (?P<player_id>\d+)"),
        re.compile(
            r"challenge (?P<action>change) (?P<challenge_id>\d+) "
            r"F(?P<open>\d)(?P<undo>\d)(?P<pause>\d) "
            r"T(?P<tyme_system>\d+),(?P<main_time>\d+),"
            r"(?P<overtime>\d+),(?P<periods>\d+),(?P<stones>\d+),"
            r"(?P<bonus>\d+),(?P<delay>\d+)"
        ),
        re.compile(
            r"challenge (?P<action>return) (?P<player_id>\d+) "
            r"F(?P<open>\d)(?P<undo>\d)(?P<pause>\d) "
            r"T(?P<tyme_system>\d+),(?P<main_time>\d+),"
            r"(?P<overtime>\d+),(?P<periods>\d+),(?P<stones>\d+),"
            r"(?P<bonus>\d+),(?P<delay>\d+)"
        ),
        re.compile(r"challenge (?P<action>confirm) (?P<challenge_id>\d+)"),
    ],
}


class InvalidMessageError(Exception):
    pass


def parse_message(message: str) -> Tuple[str, Dict[str, Any]]:

    for message_type, patterns in MESSAGE_PATTERNS.items():
        if message.startswith(message_type):
            for pattern in patterns:
                data = pattern.match(message)

                if data:
                    return message_type, data.groupdict()

            break

    raise InvalidMessageError(message)
