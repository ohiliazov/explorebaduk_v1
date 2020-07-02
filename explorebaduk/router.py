from sanic import Sanic
from sanic.response import json
from sanic.websocket import WebSocketProtocol

app = Sanic("websocket_example")


@app.websocket('')
async def feed(request, ws):
    while True:
        data = 'hello!'
        print('Sending: ' + data)
        await ws.send(data)
        data = await ws.recv()
        print('Received: ' + data)

# /
# /room/<room_id>
# /chat/<chat_id>
# /challenge/<challenge_id>
# /game/<challenge_id>


if __name__ == "__main__":
    app.run(host="localhost", port=8080, protocol=WebSocketProtocol)
