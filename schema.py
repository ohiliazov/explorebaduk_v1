from marshmallow import (
    Schema,
    fields,
    validates,
    ValidationError,
    INCLUDE,
    EXCLUDE,
)

from constants import Target, AuthAction


class Payload(Schema):
    class Meta:
        unknown = INCLUDE
    target = fields.String(required=True)

    @validates('target')
    def validate_target(self, value):
        try:
            Target(value)
        except ValueError:
            raise ValidationError(f"Invalid target: {value}")


class AuthPayload(Schema):
    class Meta:
        unknown = INCLUDE
    auth_action = fields.String(required=True)

    @validates('auth_action')
    def validate_auth_action(self, value):
        try:
            AuthAction(value)
        except ValueError:
            raise ValidationError(f"Invalid auth_action: {value}")


class LoginPayload(Schema):
    class Meta:
        unknown = EXCLUDE
    user_id = fields.Integer(required=True)
    token = fields.String(required=True)
