import json
import logging

from explorebaduk.constants import AUTH_ACTIONS, CHALLENGE_ACTIONS
from explorebaduk.handlers.auth import handle_auth
from explorebaduk.handlers.challenge import handle_challenge

logger = logging.getLogger('explorebaduk')


async def handle_message(ws, message: str):
    try:
        json_data = json.loads(message)
        message_type = json_data.get('type')
        data = json_data.get('data')

        if message_type in AUTH_ACTIONS:
            await handle_auth(ws, message_type, data)

        elif message_type in CHALLENGE_ACTIONS:
            await handle_challenge(ws, message_type, data)

        else:
            logger.info("SKIP %s", message)

    except json.decoder.JSONDecodeError as err:
        errmsg = '%s: line %d column %d (char %d)' % (err.msg, err.lineno, err.colno, err.pos)
        message = {"status": "failure", "errors": errmsg}
        return await ws.send(json.dumps(message))
