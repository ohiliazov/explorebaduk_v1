import logging
from marshmallow import ValidationError
from pprint import pprint

from explorebaduk.exceptions import MessageHandlerError
from explorebaduk.messages import (
    LoginSchema,
    ChallengeNewSchema,
    ChallengeIdSchema,
    ChallengeStartSchema,
    GameMoveSchema,
)

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
from explorebaduk.handlers.info import (
    handle_info_players,
    handle_info_challenges,
    handle_info_games,
)
from explorebaduk.handlers.game import handle_game_move
from explorebaduk.handlers.sync import register, unregister

logger = logging.getLogger("explorebaduk")

MESSAGE_HANDLERS = {
    "auth": {"login": (LoginSchema, handle_auth_login), "logout": (None, handle_auth_logout),},
    "challenge": {
        "new": (ChallengeNewSchema, handle_challenge_new),
        "cancel": (None, handle_challenge_cancel),
        "join": (ChallengeIdSchema, handle_challenge_join),
        "leave": (ChallengeIdSchema, handle_challenge_leave),
        "start": (ChallengeStartSchema, handle_challenge_start),
    },
    "game": {"move": (GameMoveSchema, handle_game_move)},
    "info": {
        "players": (None, handle_info_players),
        "challenges": (None, handle_info_challenges),
        "games": (None, handle_info_games),
    },
}


async def handle_message(ws, message: str):
    logger.info(message)

    # TODO: add message_id somewhere here if needed
    message = message.split(" ", maxsplit=2)

    if len(message) < 2:
        return await ws.send(f"ERROR [{message}] incorrect message")

    message_type, action, *data = message
    if message_type not in MESSAGE_HANDLERS:
        return await ws.send(f"ERROR [{message_type} {action}] invalid message_type")

    if action not in MESSAGE_HANDLERS[message_type]:
        return await ws.send(f"ERROR [{message_type} {action}] invalid action")

    message_schema, message_handler = MESSAGE_HANDLERS[message_type][action]

    if message_schema and not data:
        return await ws.send(f"ERROR [{message_type} {action}] no data")

    try:
        parsed_data = message_schema().load(*data) if message_schema else {}
        pprint(parsed_data)

        await message_handler(ws, parsed_data)

    except (ValidationError, MessageHandlerError) as err:
        await ws.send(f"ERROR [{message_type} {action}] {err}")

    except Exception:
        await ws.send(f"ERROR [{message_type} {action}] unexpected")
