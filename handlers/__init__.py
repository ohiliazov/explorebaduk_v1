import json


class BaseHandler:
    def __init__(self, session, queue):
        self.session = session
        self.queue = queue

    def sync_all(self, data: dict):
        message = json.dumps(data)
        self.queue.put_nowait(message)
