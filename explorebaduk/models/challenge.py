from explorebaduk.validation import challenge_validator


class Challenge:
    def __init__(self, user, data: dict = None):
        self.user = user
        self.data = data
        self.joined = {}

    @property
    def user_id(self):
        return self.user.user_id

    @property
    def user_ws(self):
        return self.joined.get(self.user_id)

    def join(self, user_id, ws):
        self.joined[user_id] = ws

    def leave(self, user_id):
        self.joined.pop(user_id, None)

    def select(self, user_id):
        return self.joined.get(user_id)

    def is_active(self):
        return self.data is not None

    def set(self, data: dict):
        if challenge_validator.validate(data):
            self.data = challenge_validator.normalized(data)

        return self.data

    def unset(self):
        if data := self.data:
            self.data = None

        return data

    def as_dict(self):
        return {
            "user_id": self.user_id,
            "challenge": self.data,
        }
