from marshmallow import (
    Schema,
    fields,
    validates,
    validates_schema,
    ValidationError,
    INCLUDE,
    EXCLUDE,
)

from constants import Target, UserAction, ChatAction, ChallengeAction

TARGET_ACTIONS = {
    Target.USER: UserAction,
    Target.CHAT: ChatAction,
    Target.CHALLENGE: ChallengeAction,
}


class WebSocketMessage(Schema):
    class Meta:
        unknown = INCLUDE
    target = fields.String(required=True)
    action = fields.String(required=True)

    @validates('target')
    def validate_target(self, value):
        try:
            Target(value)
        except ValueError:
            raise ValidationError(f"Invalid target")

    @validates_schema
    def validate_action(self, data, **kwargs):
        target = Target(data['target'])
        try:
            TARGET_ACTIONS[target](data['action'])
        except ValueError:
            raise ValidationError(f"Invalid action")


class LoginMessage(Schema):
    class Meta:
        unknown = EXCLUDE
    user_id = fields.Integer(required=True)
    token = fields.String(required=True)
