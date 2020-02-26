import logging

from explorebaduk.exceptions import InvalidMessageError
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
from explorebaduk.message import parse_message_v2

logger = logging.getLogger("explorebaduk")

MESSAGE_HANDLERS = {
    "auth": {"login": handle_auth_login, "logout": handle_auth_logout,},
    "challenge": {
        "new": handle_challenge_new,
        "cancel": handle_challenge_cancel,
        "join": handle_challenge_join,
        "leave": handle_challenge_leave,
        "start": handle_challenge_start,
    },
}


async def handle_message_v2(ws, message: str):
    logger.info("handle_message_v2")
    try:
        message_type, action, data = parse_message_v2(message)
        message_handler = MESSAGE_HANDLERS[message_type][action]
        await message_handler(ws, data)
    except InvalidMessageError as err:
        await ws.send(f"invalid message: {err}")
