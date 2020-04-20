import asyncio
import random

from explorebaduk.database import db
from explorebaduk.exceptions import MessageHandlerError
from explorebaduk.helpers import get_player_by_id, get_challenge_by_id, get_game_by_id, send_sync_messages
from explorebaduk.models import Game
from explorebaduk.models.game import GamePlayer, GameManager
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
    game = Game(challenge)
    black, white = random.sample([player, opponent], 2)
    black_player = GamePlayer(game.game_id, black.id, challenge.time_control)
    white_player = GamePlayer(game.game_id, white.id, challenge.time_control)
    game_manager = GameManager(game, black_player, white_player)

    GAMES.add(game_manager)
    CHALLENGES.remove(challenge)

    await asyncio.gather(
        player.send(f"OK [game start] {game}"),
        opponent.send(f"game started {game}"),
        send_sync_messages(f"games add {game}"),
    )

    game_manager.black.start_timer()

    await asyncio.sleep(5)
    print(game_manager.black.stop_timer())


async def handle_game_move(ws, data: dict):
    player = PLAYERS.get(ws)

    if not player:
        raise MessageHandlerError("not logged in")

    game = get_game_by_id(data["game_id"])

    if player is not game.current.player:
        raise MessageHandlerError("not your turn")

    move = data["move"]

    result = game.play_move(move)

    return await ws.send(f"You played {move}:\n{result}")
