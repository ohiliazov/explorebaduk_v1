import re
from marshmallow import fields

from explorebaduk.messages.base import BaseSchema


class GameStartSchema(BaseSchema):
    __pattern__ = re.compile(r"^(?P<game_id>\d+) (?P<opponent_id>\d+)$")
    game_id = fields.Integer(required=True)
    opponent_id = fields.Integer(required=True)


class GameMoveSchema(BaseSchema):
    __pattern__ = re.compile(r"^ID\[(?P<game_id>\d+)\]MV\[(?P<move>[a-z]{2}|pass)\]$")
    game_id = fields.Integer(required=True)
    move = fields.String(required=True)
