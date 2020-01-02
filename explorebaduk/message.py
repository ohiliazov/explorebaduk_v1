import re
from typing import Tuple, Dict, Any


MESSAGE_PATTERNS = {
    'login': re.compile(r"login (?P<username>\w+) (?P<token>\w{64})"),
    'logout': re.compile(r"logout"),
    'new': re.compile(r"new T(?P<game_type>\d)R(?P<ruleset>\d)"
                      r"F(?P<no_undo>\d)(?P<no_pause>\d)(?P<no_analyze>\d)(?P<is_private>\d) "
                      r"(?P<board_size>\d{,2}(?::\d{,2})?) "
                      r"(?P<to_join>\d+) "
                      r"(?P<tyme_system>\d)"
                      r"(?:M(?P<main_time>\d+))?"
                      r"(?:O(?P<overtime>\d+))?"
                      r"(?:P(?P<periods>\d+))?"
                      r"(?:S(?P<stones>\d+))?"
                      r"(?:B(?P<bonus>\d+))?"
                      r"(?:D(?P<delay>\d+))?")
}


class InvalidMessageError(Exception):
    pass


def parse_message(message: str) -> Tuple[str, Dict[str, Any]]:

    for message_type, pattern in MESSAGE_PATTERNS.items():
        if message.startswith(message_type):
            data = MESSAGE_PATTERNS[message_type].match(message)

            if data:
                return message_type, data.groupdict()

            break

    raise InvalidMessageError(message)


