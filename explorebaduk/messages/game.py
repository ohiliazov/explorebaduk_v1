import re
from marshmallow import fields

from explorebaduk.messages.base import BaseSchema


class GameMoveSchema(BaseSchema):
    __pattern__ = re.compile(r"^ID\[(?P<game_id>\d+)\]MV\[(?P<pos>[a-z]{2}|pass)\]$")
    game_id = fields.Integer(required=True)
    pos = fields.String(required=True)
