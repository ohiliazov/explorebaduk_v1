import asyncio
import random

from explorebaduk.database import DatabaseHandler
from explorebaduk.exceptions import MessageHandlerError
from explorebaduk.helpers import get_user_by_id, get_challenge_by_id, get_game_by_id, send_sync_messages
from explorebaduk.server import USERS, CHALLENGES, GAMES
from explorebaduk.models import Game, GameInfo


async def handle_game_start(ws, data: dict, db_handler: DatabaseHandler):
    """Start game from challenge"""
    player = USERS.get(ws)

    if not player:
        raise MessageHandlerError("not logged in")

    challenge = get_challenge_by_id(player.id)

    if not challenge:
        raise MessageHandlerError("challenge not found")

    # only creator can start the game
    if player is not challenge.creator:
        raise MessageHandlerError("not creator")

    opponent = get_user_by_id(data["opponent_id"])

    # opponent should be online
    if not opponent:
        raise MessageHandlerError("player not found")

    # opponent should be in pending
    if opponent not in challenge.pending:
        return await ws.send("player not joined")

    # TODO: implement

    black, white = random.sample([player, opponent], 2)
    handicap, komi = 0, 6.5
    game = Game(challenge, black, white, handicap, komi)

    await game.start_game(db_handler)

    GAMES.add(game)
    CHALLENGES.remove(challenge)

    await asyncio.gather(
        player.send(f"OK [game start] {game}"),
        opponent.send(f"game started {game}"),
        send_sync_messages(f"games add {game}"),
    )


async def handle_game_move(ws, data: dict, db_handler: DatabaseHandler):
    player = USERS.get(ws)

    if not player:
        raise MessageHandlerError("not logged in")

    game = get_game_by_id(data["game_id"])

    if not game:
        raise MessageHandlerError("game not found")

    if player is not game.whose_turn.player:
        raise MessageHandlerError("not your turn")

    move = data["move"]

    await game.make_move(move)
    await ws.send(str(game.kifu))


async def handle_game_mark(ws, data, db_handler: DatabaseHandler):
    player = USERS.get(ws)

    if not player:
        raise MessageHandlerError("not logged in")

    game = get_game_by_id(data["game_id"])

    if not game:
        raise MessageHandlerError("game not found")

    if player not in [game.whose_turn.player, game.opponent.player]:
        raise MessageHandlerError("not a player")

    action = data["action"]
    coord = data["coord"]

    await game.mark_stone(action, coord)


async def handle_game_leave(ws, data, db_handler: DatabaseHandler):
    pass


async def handle_game_done(ws, data, db_handler: DatabaseHandler):
    pass


async def handle_game_resign(ws, data, db_handler: DatabaseHandler):
    pass
