import re
from typing import Tuple, Dict, Any
from explorebaduk.message.challenge import CHALLENGE_STRING, JOIN_CHALLENGE_STRING


MESSAGE_PATTERNS = {
    "auth": [
        re.compile(r"^auth (?P<action>login) (?P<token>\w{64})$"),
        re.compile(r"^auth (?P<action>logout)$"),
    ],
    "challenge": [
        re.compile(fr"^challenge (?P<action>new) {CHALLENGE_STRING}$"),
        re.compile(r"^challenge (?P<action>cancel) (?P<challenge_id>\d+)$"),
        re.compile(fr"^challenge (?P<action>join) (?P<challenge_id>\d+) {JOIN_CHALLENGE_STRING}$"),
        re.compile(r"^challenge (?P<action>leave) (?P<challenge_id>\d+)$"),
        re.compile(r"^challenge (?P<action>accept) (?P<challenge_id>\d+) (?P<player_id>\d+)$"),
        re.compile(fr"^challenge (?P<action>return) (?P<player_id>\d+) {JOIN_CHALLENGE_STRING}$"),
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
                    return (
                        message_type,
                        {key: value for key, value in data.groupdict().items() if value is not None},
                    )

            break

    raise InvalidMessageError(message)
