import json
import logging

from explorebaduk.constants import USER_ACTIONS, CHALLENGE_ACTIONS
from explorebaduk.handlers.user import handle_user
from explorebaduk.handlers.challenge import handle_challenge

logger = logging.getLogger('explorebaduk')


async def handle_message(ws, message: str):
    try:
        json_data = json.loads(message)
        action = json_data.get('action')
        data = json_data.get('data')

        if action in USER_ACTIONS:
            await handle_user(ws, action, data)
        elif action in CHALLENGE_ACTIONS:
            await handle_challenge(ws, action, data)
        else:
            logger.info("SKIP %s", message)

    except json.decoder.JSONDecodeError as err:
        errmsg = '%s: line %d column %d (char %d)' % (err.msg, err.lineno, err.colno, err.pos)
        message = {"status": "failure", "errors": errmsg}
        return await ws.send(json.dumps(message))
