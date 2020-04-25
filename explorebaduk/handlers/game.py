import asyncio
import random

from explorebaduk.exceptions import MessageHandlerError
from explorebaduk.helpers import get_player_by_id, get_challenge_by_id, get_game_by_id, send_sync_messages
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
    game = challenge.game

    black, white = random.sample([player, opponent], 2)

    game.start_game(black, white, 0, 6.5)

    GAMES.add(game)
    CHALLENGES.remove(challenge)

    await asyncio.gather(
        player.send(f"OK [game start] {game}"),
        opponent.send(f"game started {game}"),
        send_sync_messages(f"games add {game}"),
    )

    await game.sync_timers()


async def handle_game_move(ws, data: dict):
    player = PLAYERS.get(ws)

    if not player:
        raise MessageHandlerError("not logged in")

    game = get_game_by_id(data["game_id"])

    if player is not game.whose_turn.player:
        raise MessageHandlerError("not your turn")

    move = data["move"]

    if not game.sgf.is_valid_move(move):
        raise MessageHandlerError(f"invalid move {move}")

    game.make_move(move)

    await game.sync_timers()

