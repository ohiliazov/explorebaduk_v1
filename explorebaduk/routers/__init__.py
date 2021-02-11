from fastapi import APIRouter

from . import challenges, players, websocket

api_router = APIRouter(prefix="/api")
api_router.include_router(players.router)
api_router.include_router(challenges.router)

ws_router = APIRouter(prefix="/ws")
ws_router.include_router(websocket.router)
