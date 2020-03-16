import asyncio
import random

from explorebaduk.exceptions import MessageHandlerError
from explorebaduk.helpers import get_player_by_id, get_challenge_by_id, get_game_by_id, send_sync_messages
from explorebaduk.models import Game
from explorebaduk.server import PLAYERS, CHALLENGES, GAMES


async def handle_game_start(ws, data: dict):
    """Start game from challenge"""
    player = PLAYERS.get(ws)

    if not player:
        raise MessageHandlerError("not logged in")

    challenge = get_challenge_by_id(player.id)

    if not challenge:
        raise MessageHandlerError("challenge not found")

    # only creator can start the game
    if player is not challenge.creator:
        raise MessageHandlerError("not creator")

    opponent = get_player_by_id(data["opponent_id"])

    # opponent should be online
    if not opponent:
        raise MessageHandlerError("player not found")

    # opponent should be in pending
    if opponent not in challenge.pending:
        return await ws.send("player not joined")

    # TODO: implement
    black, white = random.sample([player, opponent], 2)
    game = Game(player.id, black, white, challenge)
    game.black.start_timer()
    GAMES.add(game)

    CHALLENGES.remove(challenge)

    creator_color = "black" if game.black.player is player else "white"
    opponent_color = "black" if game.black.player is opponent else "white"

    await asyncio.gather(
        player.send(f"game started {challenge} {creator_color}"),
        opponent.send(f"game started {challenge} {opponent_color}"),
        send_sync_messages(f"game started {game}"),
    )


async def handle_game_move(ws, data: dict):
    player = PLAYERS.get(ws)

    if not player:
        raise MessageHandlerError("not logged in")

    game = get_game_by_id(data["game_id"])

    if player is not game.current_player:
        raise MessageHandlerError("not your turn")

    move = data["move"]

    return await ws.send(f"You played {move}")
