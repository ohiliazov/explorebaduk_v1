import re
from typing import Tuple, Dict, Any
from explorebaduk.message.challenge import CHALLENGE_STRING


MESSAGE_PATTERNS = {
    "auth": [re.compile(r"^auth (?P<action>login) (?P<token>\w{64})$"), re.compile(r"^auth (?P<action>logout)$")],
    "challenge": [
        re.compile(fr"^challenge (?P<action>new) {CHALLENGE_STRING}$"),
        re.compile(r"^challenge (?P<action>cancel) (?P<challenge_id>\d+)$"),
        re.compile(r"^challenge (?P<action>join) (?P<challenge_id>\d+)$"),
        re.compile(r"^challenge (?P<action>leave) (?P<challenge_id>\d+)$"),
    ],
    "game": [
        re.compile(r"^game (?P<action>start) (?P<challenge_id>\d+) (?P<opponent_id>\d+)$"),
        re.compile(r"^game (?P<action>play) (?P<game_id>\d+) (?P<move>[a-zA-Z]{2})$"),
        re.compile(r"^game (?P<action>undo) (?P<game_id>\d+)$"),
        re.compile(r"^game (?P<action>pass) (?P<game_id>\d+)$"),
        re.compile(r"^game (?P<action>resign) (?P<game_id>\d+)$"),
        re.compile(r"^game (?P<action>join) (?P<game_id>\d+)$"),
        re.compile(r"^game (?P<action>leave) (?P<game_id>\d+)$"),
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
