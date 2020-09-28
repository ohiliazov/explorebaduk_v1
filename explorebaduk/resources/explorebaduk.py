import asyncio
from typing import Iterable, Union
import simplejson as json

from websockets import WebSocketCommonProtocol


async def send_json(ws_list: Union[WebSocketCommonProtocol, Iterable[WebSocketCommonProtocol]], data: dict):
    if isinstance(ws_list, WebSocketCommonProtocol):
        ws_list = {ws_list}

    payload = json.dumps(data, indent=2)
    await asyncio.gather(*[ws.send(payload) for ws in ws_list])


class ExploreBadukPlayers:
    players = set()


class ExploreBadukChallenges:
    challenges = {}


class ExploreBadukGames:
    games = {}
