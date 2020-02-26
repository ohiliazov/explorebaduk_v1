import re
from typing import Tuple
from explorebaduk.message.challenge import CHALLENGE_STRING
from explorebaduk.exceptions import InvalidMessageError
from explorebaduk.schema import LoginSchema, ChallengeNewSchema, ChallengeIdSchema, ChallengeStartSchema

MESSAGE_ACTION_REGEX = {
    "auth": {
        "login": LoginSchema,
        "logout": None
    },
    "challenge": {
        "new": ChallengeNewSchema,
        "cancel": ChallengeIdSchema,
        "join": ChallengeIdSchema,
        "leave": ChallengeIdSchema,
        "start": ChallengeStartSchema,
    },
}


def parse_message_v2(message: str) -> Tuple[str, str, dict]:
    try:
        message_type, action, *data = message.split(maxsplit=2)
        message_schema = MESSAGE_ACTION_REGEX[message_type][action]
        parsed_data = message_schema().load(*data) if message_schema else {}

    except (ValueError, KeyError, IndexError, AttributeError):
        raise InvalidMessageError(message)

    return message_type, action, parsed_data
