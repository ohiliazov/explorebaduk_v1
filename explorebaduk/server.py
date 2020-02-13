from websockets import WebSocketServerProtocol

from typing import Dict, Set, Optional
from config import DATABASE_URI
from explorebaduk.database import create_session
from explorebaduk.models import Player, Challenge, Game


db = create_session(DATABASE_URI)

CONNECTED: Set[WebSocketServerProtocol] = set()
PLAYERS: Dict[WebSocketServerProtocol, Optional[Player]] = {}
LOBBY: Dict[WebSocketServerProtocol, Dict] = {}
CHALLENGES: Dict[int, Challenge] = {}
GAMES: Dict[int, Game] = {}
