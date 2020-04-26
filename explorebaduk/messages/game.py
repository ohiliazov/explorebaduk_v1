import re
from marshmallow import fields

from explorebaduk.messages.base import BaseSchema


class GameStartSchema(BaseSchema):
    __pattern__ = re.compile(r"^(?P<game_id>\d+) (?P<opponent_id>\d+)$")
    game_id = fields.Integer(required=True)
    opponent_id = fields.Integer(required=True)


class GameMoveSchema(BaseSchema):
    __pattern__ = re.compile(r"^(?P<game_id>\d+) (?P<color>[BW])\[(?P<move>[a-z]{2})?\]$")
    game_id = fields.Integer(required=True)
    color = fields.String(required=True)
    move = fields.String(missing=None)
