import logging
from pprint import pprint

from explorebaduk.schema import LoginSchema, ChallengeNewSchema, ChallengeIdSchema, ChallengeStartSchema

from marshmallow import ValidationError
from explorebaduk.handlers.auth import (
    handle_auth_login,
    handle_auth_logout,
)
from explorebaduk.handlers.challenge import (
    handle_challenge_new,
    handle_challenge_cancel,
    handle_challenge_join,
    handle_challenge_leave,
    handle_challenge_start,
)

logger = logging.getLogger("explorebaduk")

MESSAGE_HANDLERS = {
    "auth": {
        "login": (LoginSchema, handle_auth_login),
        "logout": (None, handle_auth_logout),
    },
    "challenge": {
        "new": (ChallengeNewSchema, handle_challenge_new),
        "cancel": (ChallengeIdSchema, handle_challenge_cancel),
        "join": (ChallengeIdSchema, handle_challenge_join),
        "leave": (ChallengeIdSchema, handle_challenge_leave),
        "start": (ChallengeStartSchema, handle_challenge_start),
    },
}


async def handle_message(ws, message: str):
    logger.info(message)

    message = message.split(' ', maxsplit=2)

    if len(message) < 2:
        return await ws.send("incorrect message")

    message_type, action, *data = message
    if message_type not in MESSAGE_HANDLERS:
        return await ws.send("incorrect message_type")

    if action not in MESSAGE_HANDLERS[message_type]:
        return await ws.send("incorrect action")

    message_schema, message_handler = MESSAGE_HANDLERS[message_type][action]

    if message_schema and not data:
        return await ws.send(f"no data provided")

    try:
        parsed_data = message_schema().load(*data) if message_schema else {}
        pprint(parsed_data)

        await message_handler(ws, parsed_data)

    except ValidationError as err:
        await ws.send(f"validation error {err}")

    except Exception as err:
        await ws.send(f"unexpected error {err}")
