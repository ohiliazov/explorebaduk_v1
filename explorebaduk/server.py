from websockets import WebSocketServerProtocol
from typing import Dict, Set, Optional

CONNECTED: Set[WebSocketServerProtocol] = set()
PLAYERS: Dict[WebSocketServerProtocol, Optional["Player"]] = {}
CHALLENGES: Set["Challenge"] = set()
GAMES: Set["GameManager"] = set()
LOBBY: Dict[WebSocketServerProtocol, Dict] = {}
