import asyncio


class Room:
    def __init__(self, ws_list=None):
        self.ws_list = ws_list or []

    def add(self, ws):
        self.ws_list.append(ws)

    def remove(self, ws):
        self.ws_list.pop(ws)

    async def send_all(self, message: str):
        await asyncio.gather(*[ws.send(message) for ws in self.ws_list])
