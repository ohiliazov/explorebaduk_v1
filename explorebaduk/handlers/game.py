import asyncio
import logging

from explorebaduk.constants import GameAction
from explorebaduk.models import Game
from explorebaduk.server import PLAYERS, CHALLENGES, GAMES
from explorebaduk.helpers import get_player_by_id

logger = logging.getLogger("matchmaker")


async def validate_user(ws):
    pass


async def start_game(ws, data: dict):
    logger.info("start_game")
    # Step 1. Validate users
    challenge_id = data["challenge_id"]
    challenge = CHALLENGES.get(challenge_id)

    if not challenge:
        return await ws.send("Challenge does not exist")

    player = challenge.creator

    if ws is not player.ws:
        return await ws.send("Cheat attempt!")

    opponent_id = data["opponent_id"]
    opponent = get_player_by_id(opponent_id)

    if not opponent:
        return await ws.send("Opponent not found")

    if opponent not in challenge.pending:
        return await ws.send("Opponent not in pending")

    # TODO: implement
    game = Game.from_challenge(challenge, opponent)
    game.black.start_timer()

    return asyncio.gather(player.send(f"game start {challenge} against {opponent}"),
                          opponent.send(f"game start {challenge} against {player}"))


async def handle_game(ws, data: dict):
    logger.info("handle_game")

    action = GameAction(data.pop("action"))

    if action is GameAction.START:
        await start_game(ws, data)

    else:
        return await ws.send(f"ERROR auth {action.value}: not implemented")
