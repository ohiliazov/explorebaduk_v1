import queue
from typing import List

from starlette.testclient import WebSocketTestSession


def receive_messages(websocket: WebSocketTestSession) -> List[dict]:
    messages = []

    while True:
        try:
            messages.append(websocket.receive_json(timeout=0.5))
        except queue.Empty:
            break

    return messages
