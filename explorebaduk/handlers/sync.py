import asyncio
from explorebaduk.server import USERS, CHALLENGES, GAMES
from explorebaduk.handlers import handle_info_players, handle_info_challenges, handle_info_games
from explorebaduk.helpers import get_challenge_by_id, get_game_by_id, send_sync_messages


async def register(ws):
    USERS[ws] = None
    await asyncio.gather(
        handle_info_players(ws), handle_info_challenges(ws), handle_info_games(ws),
    )


async def unregister(ws):
    sync_messages = []
    user = USERS.pop(ws)
    if user:
        sync_messages.append(f"players del {user}")
        challenge = get_challenge_by_id(user.id)

        if challenge:
            CHALLENGES.remove(challenge)
            sync_messages.append(f"challenges del {challenge}")

        game = get_game_by_id(user.id)
        if game:
            GAMES.remove(game)
            sync_messages.append(f"games del {game}")

        await send_sync_messages(sync_messages)
