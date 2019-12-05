from marshmallow import (
    Schema,
    fields,
    validates_schema,
    ValidationError,
    INCLUDE,
    EXCLUDE,
)

from actions import VALID_ACTIONS


class WebSocketMessage(Schema):
    class Meta:
        unknown = INCLUDE
    target = fields.String(required=True)
    action = fields.String(required=True)

    @validates_schema
    def validate_action(self, data, **kwargs):
        valid_actions = VALID_ACTIONS.get(data['target'])

        if not valid_actions:
            raise ValidationError(f"Invalid target")

        if not data['action'] in valid_actions:
            raise ValidationError(f"Invalid action")


class LoginMessage(Schema):
    class Meta:
        unknown = EXCLUDE
    user_id = fields.Integer(required=True)
    token = fields.String(required=True)
