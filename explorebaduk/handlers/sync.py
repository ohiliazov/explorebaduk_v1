import asyncio
from explorebaduk.server import CONNECTED, PLAYERS, CHALLENGES
from explorebaduk.handlers import handle_info_players, handle_info_challenges, handle_info_games, handle_auth_logout, handle_challenge_cancel
from explorebaduk.helpers import get_challenge_by_id

async def register(ws):
    CONNECTED.add(ws)
    await asyncio.gather(
        handle_info_players(ws, {}),
        handle_info_challenges(ws, {}),
        handle_info_games(ws, {}),
    )


async def unregister(ws):
    if ws in PLAYERS:
        player = PLAYERS[ws]
        challenge = get_challenge_by_id(player.id)

        if challenge:
            await handle_challenge_cancel(ws, )

        await handle_auth_logout(ws, {})

    CONNECTED.remove(ws)
