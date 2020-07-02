import re
from marshmallow import fields

from explorebaduk.messages.base import BaseSchema


class LoginSchema(BaseSchema):
    __pattern__ = re.compile(r"^(?P<token>\w{64})$")

    token = fields.String(required=True)
