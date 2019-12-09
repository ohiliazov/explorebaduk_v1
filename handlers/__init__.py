import json
from constants import SYNC_PRIORITY


class InvalidActionError(Exception):
    pass


class BaseHandler:
    PRIORITY = NotImplemented

    def __init__(self, session, sync_queue):
        self.session = session
        self.sync_queue = sync_queue

    def send(self, ws, data: dict):
        self.sync_queue.put_nowait((self.PRIORITY, (ws, data)))

    def sync(self, data: dict):
        self.sync_queue.put_nowait((SYNC_PRIORITY, (None, data)))

    def handle_action(self, ws, action: str, data: dict):
        raise NotImplementedError("handle_action is not implemented")
