import asyncio
from explorebaduk.server import CONNECTED, PLAYERS, CHALLENGES, GAMES
from explorebaduk.handlers import handle_info_players, handle_info_challenges, handle_info_games
from explorebaduk.helpers import get_challenge_by_id, get_game_by_id, send_sync_messages


async def register(ws):
    CONNECTED.add(ws)
    await asyncio.gather(
        handle_info_players(ws, {}), handle_info_challenges(ws, {}), handle_info_games(ws, {}),
    )


async def unregister(ws):
    CONNECTED.remove(ws)

    sync_messages = []
    if ws in PLAYERS:
        player = PLAYERS[ws]
        sync_messages.append(f"players del {player}")
        challenge = get_challenge_by_id(player.id)

        if challenge:
            CHALLENGES.remove(challenge)
            sync_messages.append(f"challenges del {challenge}")

        game = get_game_by_id(player.id)
        if game:
            GAMES.remove(game)
            sync_messages.append(f"games del {game}")

        await send_sync_messages(sync_messages)
