import asyncio
import json
import websockets
import logging

from explorebaduk import config
from explorebaduk.server import eb_server
from explorebaduk.handlers import handle_message


logger = logging.getLogger('explorebaduk')


async def sync_worker():
    while True:
        ws, data = await eb_server.sync_queue.get()
        message = json.dumps(data)

        if ws:
            await ws.send(message)

        elif eb_server.clients:
            await asyncio.wait([ws.send(message) for ws in eb_server.clients])

        logger.debug("OUT >> %s", message)
        eb_server.sync_queue.task_done()


async def start_server(ws: websockets.WebSocketServerProtocol, path: str):
    await eb_server.sync_user(ws)
    try:
        async for message in ws:
            logger.debug("IN <<< %s", message)
            await handle_message(ws, message)
    except websockets.WebSocketException:
        pass
    finally:
        await eb_server.goodbye_user(ws)


def serve():
    server = websockets.serve(start_server, config.SERVER_HOST, config.SERVER_PORT)
    eb_server.add_ws_server(server.ws_server)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(server)
    loop.run_until_complete(sync_worker())
    loop.run_forever()


if __name__ == '__main__':
    serve()
