from explorebaduk.constants import EventName
from explorebaduk.messages import (
    ChallengesAddMessage,
    ChallengesRemoveMessage,
    ErrorMessage,
    MessageBase,
)
from explorebaduk.resources import Feed
from explorebaduk.validation import create_game_schema, validate_payload


class Challenge:
    def __init__(self, owner_ws, data: dict = None):
        self.owner_ws = owner_ws
        self.data = data
        self.joined = set()

    def __bool__(self):
        return self.data is not None

    def set(self, data):
        self.data = data

    def unset(self):
        self.data = None


class ChallengeFeed(Feed):
    def __init__(self, request, ws, challenge_id):
        super().__init__(request, ws)
        self.challenge_id = challenge_id

    @property
    def feed_name(self) -> str:
        return f"challenges__{self.challenge_id}"

    @property
    def handlers(self) -> dict:
        return {
            EventName.CHALLENGE_SET: self.set_challenge,
            EventName.CHALLENGE_UNSET: self.unset_challenge,
            EventName.CHALLENGE_JOIN: self.join_challenge,
            EventName.CHALLENGE_LEAVE: self.leave_challenge,
        }

    def is_owner(self):
        return self.conn.authorized and self.challenge_id == self.conn.user_id

    @property
    def challenge(self):
        return self.app.challenges.get(self.challenge_id)

    @property
    def joined(self):
        if self.challenge:
            return self.challenge.joined

    async def broadcast_to_challenges(self, message: MessageBase):
        await self.broadcast(message, feed_name="challenges")

    async def send_to_owner(self, event, data):
        await self.notify_user(event, data, user_id=self.challenge_id)

    async def initialize(self):
        if self.conn.authorized and self.is_owner():
            self.app.challenges[self.challenge_id] = Challenge(self.ws)

    async def finalize(self):
        if self.challenge is None:
            return

        if self.is_owner():
            self.app.challenges.pop(self.challenge_id)
            await self.broadcast_to_challenges(ChallengesRemoveMessage(self.challenge_id))

        elif self.conn.user_id in self.joined and not len(self.get_user_connections()):
            self.joined.remove(self.conn.user_id)
            await self.send_to_owner(EventName.CHALLENGE_LEAVE, {"user_id": self.conn.user_id})
            await self.notify_user(EventName.CHALLENGE_LEAVE, {"message": "Left"})

    async def set_challenge(self, data):
        if not self.conn.authorized:
            return await self.conn.send_message(ErrorMessage("Already authorized"))

        if not self.is_owner():
            return await self.conn.send_message(ErrorMessage("Not challenge owner"))

        challenge, errors = validate_payload(data, create_game_schema)

        if errors:
            return await self.conn.send(EventName.ERROR, errors)

        if self.challenge:
            await self.unset_challenge()

        self.challenge.set(challenge)

        await self.broadcast_to_challenges(ChallengesAddMessage(self.challenge_id, self.challenge.data))
        await self.notify_all(EventName.CHALLENGE_SET, {"message": "Challenge set"})

    async def unset_challenge(self, data=None):
        if not self.conn.authorized:
            return await self.conn.send_message(ErrorMessage("Not authorized"))

        if not self.is_owner():
            return await self.conn.send_message(ErrorMessage("Not challenge owner"))

        if not self.challenge:
            return await self.conn.send_message(ErrorMessage("Challenge not set"))

        self.challenge.unset()

        await self.broadcast_to_challenges(ChallengesRemoveMessage(self.challenge_id))
        await self.notify_all(EventName.CHALLENGE_UNSET, {"message": "Challenge unset"})

    async def join_challenge(self, data):
        if not self.conn.authorized:
            return await self.conn.send_message(ErrorMessage("Not authorized"))

        if self.is_owner():
            return await self.conn.send_message(ErrorMessage("You are the owner!"))

        if not self.challenge:
            return await self.conn.send_message(ErrorMessage("Challenge not set"))

        self.joined.add(self.conn.user_id)
        await self.send_to_owner(EventName.CHALLENGE_JOIN, self.conn.user.as_dict())
        await self.notify_user(EventName.CHALLENGE_JOIN, {"message": "Joined"})

    async def leave_challenge(self, data):
        if not self.conn.authorized:
            return await self.conn.send_message(ErrorMessage("Not authorized"))

        if self.is_owner():
            return await self.conn.send_message(ErrorMessage("You are the owner!"))

        if not self.challenge:
            return await self.conn.send_message(ErrorMessage("Challenge not set"))

        if self.conn.user_id not in self.joined:
            return await self.conn.send_message(ErrorMessage("Not joined"))

        self.joined.remove(self.conn.user_id)
        await self.send_to_owner(EventName.CHALLENGE_LEAVE, {"user_id": self.conn.user_id})
        await self.notify_user(EventName.CHALLENGE_LEAVE, {"message": "Left"})
