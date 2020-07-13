import asyncio
from enum import Enum
from typing import List, Union, Type, Any

from marshmallow import validate, ValidationError

from explorebaduk.models import User, Challenge, Game

USERS = {}
CHALLENGES = {}
GAMES = {}


class EnumValidator(validate.Validator):
    """Validator which succeeds if the enumerator contains value.

    :param enum: The enumerator which should contain given value.
    """

    def __init__(self, enum: Type[Enum] = None):
        self.enum = enum

    def _repr_args(self) -> str:
        return "enum={!r}".format(self.enum.__name__)

    def __call__(self, value) -> Any:
        try:
            self.enum(value)
        except ValueError:
            raise ValidationError(f"'{value!r}' is not a valid {self.enum.__name__}.")

        return value


def get_user_by_id(player_id: int) -> User:
    for player in USERS.values():
        if player.id == player_id:
            return player


def get_challenge_by_id(player_id: int) -> Challenge:
    for challenge in CHALLENGES:
        if challenge.creator.id == player_id:
            return challenge


def get_game_by_id(game_id: int) -> Game:
    for game in GAMES:
        if game.game_id == game_id:
            return game


async def send_messages(ws, messages: Union[str, List[str]]):
    if isinstance(messages, str):
        messages = [messages]

    if ws in USERS:
        await asyncio.gather(*[ws.send(message) for message in messages])


async def send_sync_messages(messages: Union[str, List[str]]):
    if isinstance(messages, str):
        messages = [messages]

    if USERS:
        await asyncio.gather(*[send_messages(ws, messages) for ws in USERS])
