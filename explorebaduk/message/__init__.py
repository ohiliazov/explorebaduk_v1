import re
from typing import Tuple
from explorebaduk.message.challenge import CHALLENGE_STRING
from explorebaduk.exceptions import InvalidMessageError


MESSAGE_ACTION_REGEX = {
    "auth": {"login": re.compile(r"^(?P<token>\w{64})$"), "logout": None},
    "challenge": {
        "new": re.compile(fr"^{CHALLENGE_STRING}$"),
        "cancel": re.compile(r"^(?P<challenge_id>\d+)$"),
        "join": re.compile(r"^(?P<challenge_id>\d+)$"),
        "leave": re.compile(r"^(?P<challenge_id>\d+)$"),
        "start": re.compile(r"^(?P<challenge_id>\d+) (?P<opponent_id>\d+)$"),
    },
}


def parse_message_v2(message: str) -> Tuple[str, str, dict]:
    try:
        message_type, action, *data = message.split(maxsplit=2)
        message_pattern = MESSAGE_ACTION_REGEX[message_type][action]
        parsed_data = message_pattern.match(data[0]).groupdict() if message_pattern else {}

    except (ValueError, KeyError, IndexError, AttributeError):
        raise InvalidMessageError(message)

    return message_type, action, parsed_data
