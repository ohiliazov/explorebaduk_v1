import asyncio
from typing import List, Union
from explorebaduk.server import CONNECTED


async def send_messages(ws, messages: Union[str, List[str]]):
    if isinstance(messages, str):
        messages = [messages]
    if ws in CONNECTED:
        await asyncio.gather(*[ws.send(message) for message in messages])


async def send_sync_messages(messages: Union[str, List[str]]):
    if CONNECTED:
        await asyncio.gather(*[send_messages(ws, messages) for ws in CONNECTED])
