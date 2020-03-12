import re
from marshmallow import fields, validate

from explorebaduk.messages.base import BaseSchema


class LoginSchema(BaseSchema):
    __pattern__ = re.compile(r"^(?P<token>\w{64})$")

    token = fields.String(required=True, validate=validate.Length(equal=64))
