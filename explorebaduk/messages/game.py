import re
from marshmallow import fields

from explorebaduk.messages.base import BaseSchema


# game leave 777
# game move 777 dd
# game resign 777
# game mark 777 sx
# game done 777

class GameIDSchema(BaseSchema):
    __pattern__ = re.compile(r"^(?P<game_id>\d+)$")
    game_id = fields.Integer(required=True)


class GameStartSchema(BaseSchema):
    __pattern__ = re.compile(r"^(?P<game_id>\d+) (?P<opponent_id>\d+)$")
    game_id = fields.Integer(required=True)
    opponent_id = fields.Integer(required=True)


class GameMoveSchema(BaseSchema):
    __pattern__ = re.compile(r"^(?P<game_id>\d+) (?P<move>[a-z]{2}|pass)$")
    game_id = fields.Integer(required=True)
    move = fields.String(missing=None)


class GameMarkSchema(BaseSchema):
    __pattern__ = re.compile(r"^(?P<game_id>\d+) (?P<coord>[a-z]{2})$")
    game_id = fields.Integer(required=True)
    coord = fields.String(required=True)
