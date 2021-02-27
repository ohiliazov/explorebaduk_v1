from fastapi import APIRouter

from . import games, players, websocket

api_router = APIRouter(prefix="/api")
api_router.include_router(players.router)
api_router.include_router(games.router)

ws_router = APIRouter(prefix="/ws")
ws_router.include_router(websocket.router)
