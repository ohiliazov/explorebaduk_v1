from fastapi import APIRouter

from . import friends, game_invites, open_games, players, websocket

api_router = APIRouter(prefix="/api")
api_router.include_router(players.router)
api_router.include_router(friends.router)
api_router.include_router(open_games.router)
api_router.include_router(game_invites.router)

ws_router = APIRouter(prefix="/ws")
ws_router.include_router(websocket.router)
