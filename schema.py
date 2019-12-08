from marshmallow import Schema, fields


class LoginSchema(Schema):
    user_id = fields.Integer(required=True)
    token = fields.String(required=True)
