import json
import logging

from explorebaduk.constants import LOGIN, LOGOUT, CHALLENGE
from explorebaduk.exceptions import AuthenticationError, InvalidMessageError
from explorebaduk.handlers.auth import handle_login, handle_logout
from explorebaduk.handlers.challenge import handle_challenge

logger = logging.getLogger('explorebaduk')


async def handle_message(ws, message: str):
    try:
        json_data = json.loads(message)
        message_type = json_data.get('type')
        data = json_data.get('data') or {}

        if message_type == LOGIN:
            await handle_login(ws, data)

        elif message_type == LOGOUT:
            await handle_logout(ws)

        elif message_type in CHALLENGE:
            action = json_data.get('action')
            await handle_challenge(ws, action, data)

        else:
            logger.info("SKIP %s", message)

    except json.decoder.JSONDecodeError as err:
        errmsg = '%s: line %d column %d (char %d)' % (err.msg, err.lineno, err.colno, err.pos)
        message = {"status": "failure", "errors": errmsg}
        return await ws.send(json.dumps(message))

    except (AuthenticationError, InvalidMessageError) as err:
        message = {"status": "failure", "errors": str(err)}
        return await ws.send(json.dumps(message))
