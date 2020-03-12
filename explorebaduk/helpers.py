import asyncio
from enum import Enum
from typing import List, Union, Type, Any

from marshmallow import validate, ValidationError

from explorebaduk.server import CONNECTED, PLAYERS, CHALLENGES


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


def get_player_by_id(player_id: int):
    for player in PLAYERS.values():
        if player.id == player_id:
            return player


def get_challenge_by_id(challenge_id: int):
    for challenge in CHALLENGES:
        if challenge.challenge_id == challenge_id:
            return challenge


def error_message(message_type, action, reason):
    return f"{message_type} {action} ERROR ({reason})"


async def send_messages(ws, messages: Union[str, List[str]]):
    if isinstance(messages, str):
        messages = [messages]

    if ws in CONNECTED:
        await asyncio.gather(*[ws.send(message) for message in messages])


async def send_sync_messages(messages: Union[str, List[str]]):
    if isinstance(messages, str):
        messages = [messages]

    if CONNECTED:
        await asyncio.gather(*[send_messages(ws, messages) for ws in CONNECTED])
