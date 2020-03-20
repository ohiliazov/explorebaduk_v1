from websockets import WebSocketServerProtocol

from typing import Dict, Set, Optional
from config import DATABASE_URI
from explorebaduk.database import create_session


db = create_session(DATABASE_URI)

CONNECTED: Set[WebSocketServerProtocol] = set()
PLAYERS: Dict[WebSocketServerProtocol, Optional["Player"]] = {}
CHALLENGES: Set["Challenge"] = set()
GAMES: Set["Game"] = set()
LOBBY: Dict[WebSocketServerProtocol, Dict] = {}
