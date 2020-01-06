import json
import logging

from marshmallow import ValidationError
from explorebaduk.constants import AUTH, LOGIN, LOGOUT, CHALLENGE
from explorebaduk.exceptions import AuthenticationError, InvalidMessageError
from explorebaduk.handlers.auth import handle_auth
from explorebaduk.handlers.challenge import handle_challenge
from explorebaduk.message import parse_message, InvalidMessageError
logger = logging.getLogger('explorebaduk')


async def handle_message(ws, message: str):
    try:
        message_type, data = parse_message(message)

        if message_type == AUTH:
            return await handle_auth(ws, data)

        if message_type == CHALLENGE:
            await handle_challenge(ws, data)

        else:
            logger.info("SKIP %s", message)

    except InvalidMessageError as err:
        return await ws.send(f'ERROR: Invalid message: {err}')

    except ValidationError as err:
        return await ws.send(f'ERROR: Invalid message: {err}')

    except json.decoder.JSONDecodeError as err:
        errmsg = '%s: line %d column %d (char %d)' % (err.msg, err.lineno, err.colno, err.pos)
        message = {"status": "failure", "errors": errmsg}
        return await ws.send(json.dumps(message))

    except (AuthenticationError, InvalidMessageError) as err:
        message = {"status": "failure", "errors": str(err)}
        return await ws.send(json.dumps(message))
