import re
from typing import Tuple, Dict, Any


MESSAGE_PATTERNS = {
    'auth': [re.compile(r"auth (?P<action>login) (?P<username>\w+) (?P<token>\w{64})"),
             re.compile(r"auth (?P<action>logout)")],
    'challenge': [re.compile(r"challenge (?P<action>new) (?P<game_type>\d)R(?P<ruleset>\d)P(?P<to_join>\d+)"
                             r"U(?P<undo>\d)P(?P<pause>\d)A(?P<analyze>\d)P(?P<private>\d) "
                             r"(?P<board_size>\d{,2}(?::\d{,2})?) "
                             r"(?P<tyme_system>\d+)M(?P<main_time>\d+)O(?P<overtime>\d+)"
                             r"P(?P<periods>\d+)S(?P<stones>\d+)B(?P<bonus>\d+)D(?P<delay>\d+)")],
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
