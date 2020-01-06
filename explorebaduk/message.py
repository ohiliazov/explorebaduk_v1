import re
from typing import Tuple, Dict, Any


GAME_INFO_STRING = r"GT(?P<game_type>\d)RL(?P<rules>\d)PL(?P<players>\d+) (?P<width>\d{,2}):(?P<height>\d{,2})"
GAME_SETTINGS_STRING = (
    r"F(?P<is_open>\d)(?P<undo>\d)(?P<pause>\d) "
    r"T(?P<tyme_system>\d+)M(?P<main_time>\d+)"
    r"O(?P<overtime>\d+)P(?P<periods>\d+)S(?P<stones>\d+)"
    r"B(?P<bonus>\d+)D(?P<delay>\d+)"
)

MESSAGE_PATTERNS = {
    "auth": [
        re.compile(r"^auth (?P<action>login) (?P<user_id>\d+) (?P<token>\w{64})$"),
        re.compile(r"^auth (?P<action>logout)$"),
    ],
    "challenge": [
        re.compile(r"^challenge (?P<action>new) " + GAME_INFO_STRING + " " + GAME_SETTINGS_STRING + "$"),
        re.compile(r"^challenge (?P<action>cancel) (?P<challenge_id>\d+)$"),
        re.compile(r"^challenge (?P<action>join) (?P<challenge_id>\d+)$"),
        re.compile(r"^challenge (?P<action>leave) (?P<challenge_id>\d+)$"),
        re.compile(r"^challenge (?P<action>accept) (?P<challenge_id>\d+) (?P<player_id>\d+)$"),
        re.compile(r"^challenge (?P<action>change) (?P<challenge_id>\d+) " + GAME_SETTINGS_STRING + "$"),
        re.compile(r"^challenge (?P<action>return) (?P<player_id>\d+) " + GAME_SETTINGS_STRING + "$"),
        re.compile(r"^challenge (?P<action>confirm) (?P<challenge_id>\d+)$"),
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
