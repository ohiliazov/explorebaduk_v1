import asyncio
import logging

from explorebaduk.constants import GameAction
from explorebaduk.models import Game
from explorebaduk.server import PLAYERS, CHALLENGES, GAMES

logger = logging.getLogger("matchmaker")


async def validate_user(ws):
    pass


async def start_game(ws, data: dict):
    logger.info("start_game")
    # Step 1. Validate users
    challenge_id = data["challenge_id"]
    challenge = CHALLENGES.get(challenge_id)

    if not challenge.ready:
        return await ws.send("challenge not ready to start")

    # TODO: implement
    game = Game.from_challenge(challenge)


async def handle_game(ws, data: dict):
    logger.info("handle_challenge")

    action = GameAction(data.pop("action"))

    if action is GameAction.START:
        await start_game(ws, data)

    else:
        return await ws.send(f"ERROR auth {action.value}: not implemented")
