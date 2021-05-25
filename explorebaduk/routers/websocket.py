import asyncio

from fastapi import Depends, WebSocket, WebSocketDisconnect
from fastapi.concurrency import run_until_first_complete
from fastapi.routing import APIRouter

from explorebaduk.connection import ConnectionManager
from explorebaduk.database import DatabaseHandler
from explorebaduk.dependencies import db_handler
from explorebaduk.messages import ChallengeOpenMessage, DirectChallengeMessage, Notifier
from explorebaduk.online import UsersOnline
from explorebaduk.schemas import GameSpeed

router = APIRouter()

OFFLINE_TIMEOUT = 5


class WebsocketManager(ConnectionManager):
    async def send_messages(self):
        if self.user:
            await UsersOnline.add(self.user, self.websocket)

        messages = list(
            map(ChallengeOpenMessage, self.db.get_open_challenges()),
        )

        if self.user:
            direct_challenges = self.db.get_direct_challenges(self.user_id)
            messages.extend(map(DirectChallengeMessage, direct_challenges))

        if messages:
            await asyncio.wait([self._send(message) for message in messages])

    async def finalize(self):
        if self.user:
            await UsersOnline.remove(self.user, self.websocket)
            await asyncio.sleep(OFFLINE_TIMEOUT)

            if not UsersOnline.is_online(self.user):
                await Notifier.player_offline(self.user)

                challenges = self.db.get_challenges_from_user(self.user.user_id)

                for challenge in challenges:
                    if challenge.game.speed is GameSpeed.CORRESPONDENCE:
                        continue

                    if challenge.opponent_id:
                        await Notifier.direct_challenge_cancelled(challenge)
                    else:
                        await Notifier.challenge_cancelled(challenge)
                    self.db.session.delete(challenge)


@router.websocket("/ws")
async def ws_handler(websocket: WebSocket, db: DatabaseHandler = Depends(db_handler)):
    manager = WebsocketManager(websocket, db)
    try:
        await manager.initialize()
        await manager.send_messages()
        tasks = [
            (manager.start_receiver, {}),
            (manager.start_sender, {"channel": "main"}),
            (manager.start_sender, {"channel": f"main.{manager.username}"}),
        ]
        await run_until_first_complete(*tasks)
    except WebSocketDisconnect:
        pass
    finally:
        await manager.finalize()
