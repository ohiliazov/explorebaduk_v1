import asyncio

from fastapi import Depends, WebSocket, WebSocketDisconnect
from fastapi.concurrency import run_until_first_complete
from fastapi.routing import APIRouter

from explorebaduk.connection import ConnectionManager
from explorebaduk.database import DatabaseHandler
from explorebaduk.dependencies import db_handler
from explorebaduk.managers import (
    add_player_ws,
    get_player_ids,
    is_player_online,
    remove_player_ws,
)
from explorebaduk.messages import (
    ChallengeOpenMessage,
    DirectChallengeMessage,
    Notifier,
    PlayerOfflineMessage,
    PlayerOnlineMessage,
)
from explorebaduk.schemas import GameSpeed

router = APIRouter()

OFFLINE_TIMEOUT = 5


class WebsocketManager(ConnectionManager):
    def __init__(self, websocket, db):
        super().__init__(websocket, db)
        self.search_field = ""

    async def send_messages(self):
        was_online = is_player_online(self.user)

        if self.user:
            add_player_ws(self.user, self.websocket)

            if not was_online:
                await Notifier.player_online(self.user)

        user_ids_online = get_player_ids()
        if self.user:
            user_ids_online.remove(self.user.user_id)

        users_online = self.db.get_users(user_ids_online)
        challenges = self.db.get_open_challenges()

        users_messages = [PlayerOnlineMessage(user) for user in users_online]
        challenges_messages = [
            ChallengeOpenMessage(challenge) for challenge in challenges
        ]
        direct_challenges_messages = []

        if self.user:
            direct_challenges = self.db.get_direct_challenges(self.user_id)
            direct_challenges_messages = [
                DirectChallengeMessage(direct_challenge)
                for direct_challenge in direct_challenges
            ]

        messages = users_messages + challenges_messages + direct_challenges_messages
        if messages:
            await asyncio.wait([self._send(message) for message in messages])

    async def finalize(self):
        if self.user:
            remove_player_ws(self.user, self.websocket)
            await asyncio.sleep(OFFLINE_TIMEOUT)

            if not is_player_online(self.user):
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

    def check_player_filter(self, player_data):
        if not self.search_field:
            return True

        first_name = player_data["first_name"]
        last_name = player_data["last_name"]
        username = player_data["username"]

        if " " not in self.search_field:
            return any(
                [
                    self.search_field in first_name,
                    self.search_field in last_name,
                    self.search_field in username,
                ],
            )

        s1, s2 = self.search_field.split(" ", maxsplit=1)
        return any(
            [
                s1 in first_name and s2 in last_name,
                s2 in first_name and s1 in last_name,
            ],
        )

    async def send_notification(self, message):

        if (
            message.event
            in (
                PlayerOnlineMessage.event,
                PlayerOfflineMessage.event,
            )
            and not self.check_player_filter(message.data)
        ):
            return

        await self._send(message)

    async def process_message(self, message):
        if message.event == "players.list":
            self.search_field = message.data

        users_online = self.db.search_users(self.search_field)

        users_messages = [
            PlayerOnlineMessage(user)
            for user in users_online
            if self.check_player_filter(user.asdict())
        ]

        if users_messages:
            await asyncio.wait([self._send(message) for message in users_messages])


@router.websocket("/ws")
async def ws_handler(websocket: WebSocket, db: DatabaseHandler = Depends(db_handler)):
    manager = WebsocketManager(websocket, db)
    try:
        await manager.initialize()
        await manager.send_messages()
        tasks = [
            (manager.start_receiver, {}),
            (manager.start_sender, {"channel": "main"}),
            (manager.start_sender, {"channel": f"user.{manager.user_id}"}),
        ]
        await run_until_first_complete(*tasks)
    except WebSocketDisconnect:
        pass
    finally:
        await manager.finalize()
