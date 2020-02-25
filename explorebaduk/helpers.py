import asyncio
from typing import List, Union
from explorebaduk.server import CONNECTED, PLAYERS


def get_player_by_id(player_id):
    for player in PLAYERS.values():
        if player.id == player_id:
            return player


def error_message(message_type, action, reason):
    return f"{message_type} {action} ERROR ({reason})"


async def send_messages(ws, messages: Union[str, List[str]]):
    if isinstance(messages, str):
        messages = [messages]

    if ws in CONNECTED:
        await asyncio.gather(*[ws.send(message) for message in messages])


async def send_sync_messages(messages: Union[str, List[str]]):
    if isinstance(messages, str):
        messages = [messages]

    if CONNECTED:
        await asyncio.gather(*[send_messages(ws, messages) for ws in CONNECTED])
