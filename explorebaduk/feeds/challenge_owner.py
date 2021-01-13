from explorebaduk.resources import Feed
from explorebaduk.validation import create_game_schema, validate_payload


class ChallengeOwnerFeed(Feed):
    def __init__(self, request, ws, challenge_id):
        super().__init__(request, ws)
        self.challenge_id = challenge_id

    @property
    def feed_name(self) -> str:
        return f"challenge__{self.challenge_id}"

    @property
    def handlers(self) -> dict:
        return {
            "authorize": self.authorize,
            "challenge.set": self.set_challenge,
            "challenge.unset": self.unset_challenge,
            "challenge.join": self.join_challenge,
            "challenge.leave": self.leave_challenge,
        }

    def is_owner(self):
        return self.conn.authorized and self.challenge_id == self.conn.user_id

    @property
    def challenge(self):
        return self.app.challenges.get(self.conn.user_id)

    async def broadcast_to_challenges(self, event, data):
        await self.broadcast(event, data, feed_name="challenges")

    async def send_to_owner(self, event, data):
        for conn in self.observers:
            if conn.user_id == self.challenge_id:
                await conn.send(event, data)
        else:
            return await self.conn.send("error", {"message": "Owner not found"})

    async def authorize(self, data):
        if self.conn.authorized:
            return await self.conn.send("error", {"message": "Already authorized"})

        await self.conn.authorize(data.get("token"))

    async def set_challenge(self, data):
        if not self.is_owner():
            return await self.conn.send("set.error", {"message": "Not challenge owner"})

        challenge, errors = validate_payload(data, create_game_schema)

        if errors:
            return await self.conn.send("set.error", errors)

        if self.challenge:
            await self.unset_challenge()

        self.app.challenges[self.conn.user_id] = challenge

        await self.broadcast_to_challenges("challenges.add", {"user_id": self.conn.user_id, **challenge})
        await self.broadcast("set.ok", {"message": "Challenge set"})

    async def unset_challenge(self, data=None):
        if not self.is_owner():
            return await self.conn.send("unset.error", {"message": "Not challenge owner"})

        if not self.challenge:
            return await self.conn.send("unset.error", {"message": "Challenge not set"})

        self.app.challenges.pop(self.conn.user_id)

        await self.broadcast_to_challenges("challenges.remove", {"user_id": self.conn.user_id})
        await self.broadcast("unset.ok", {"message": "Challenge unset"})

    async def join_challenge(self, data):
        if not self.conn.authorized:
            return await self.conn.send("join.error", {"message": "Not authorized"})

        if self.is_owner():
            return await self.conn.send("join.error", {"message": "You are the owner!"})

        if not self.challenge:
            return await self.conn.send("join.error", {"message": "Challenge not set"})

        await self.send_to_owner("challenge.join", self.conn.user.as_dict())

        if "joined" not in self.challenge:
            self.challenge["joined"] = set()
        self.challenge["joined"].add(self.conn.user_id)

        await self.conn.send("join.ok", {"message": "Joined"})

    async def leave_challenge(self, data):
        if not self.conn.authorized:
            return await self.conn.send("leave.error", {"message": "Not authorized"})

        if self.is_owner():
            return await self.conn.send("leave.error", {"message": "You are the owner!"})

        if not self.challenge:
            return await self.conn.send("leave.error", {"message": "Challenge not set"})

        if self.conn.user_id not in self.challenge.get("joined"):
            return await self.conn.send("leave.error", {"message": "Not joined"})

        await self.send_to_owner("challenge.leave", {"user_id": self.conn.user_id})
        self.challenge["joined"].remove(self.conn.user_id)

        await self.conn.send("leave.ok", {"message": "Left"})

    async def finalize(self):
        if self.is_owner():
            if self.challenge:
                self.app.challenges.pop(self.conn.user_id)
                await self.broadcast_to_challenges("challenge.remove", {"user_id": self.conn.user_id})

        if self.conn.user_id in self.challenge.get("joined"):
            await self.send_to_owner("challenge.leave", {"user_id": self.conn.user_id})
            self.challenge["joined"].remove(self.conn.user_id)
