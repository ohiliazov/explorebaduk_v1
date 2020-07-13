import asyncio
import json
from asyncio import CancelledError
from sanic.request import Request
from sanic.log import logger
from websockets import WebSocketClientProtocol, ConnectionClosed


def payload_user_online(user):
    return json.dumps({
        "status": "online",
        "user_id": user.user_id,
        "last_name": user.last_name,
        "first_name": user.first_name,
        "rating": user.rating,
    })


def payload_user_offline(user):
    return json.dumps({
        "status": "offline",
        "user_id": user.user_id,
    })


async def send_player_list(request: Request, ws: WebSocketClientProtocol):
    await asyncio.gather(*[ws.send(payload_user_online(user)) for user in request.app.players.values()])


async def set_player_online(request: Request, ws: WebSocketClientProtocol):

    if user := request.ctx.user:
        payload = payload_user_online(user)
        await asyncio.gather(*[ws.send(payload) for ws in request.app.players])

        request.app.players[ws] = user
        logger.info(payload)


async def set_player_offline(request: Request, ws: WebSocketClientProtocol):
    if user := request.app.players.pop(ws, None):
        payload = payload_user_offline(user)
        await asyncio.gather(*[ws.send(payload) for ws in request.app.players])
        logger.info(payload)


async def players_feed_handler(request: Request, ws: WebSocketClientProtocol):
    await send_player_list(request, ws)
    await set_player_online(request, ws)
    try:
        await ws.recv()
    except (CancelledError, ConnectionClosed) as err:
        raise err
    finally:
        await set_player_offline(request, ws)
