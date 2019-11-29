from marshmallow import Schema, fields, validates


class PayloadBase(Schema):
    action = fields.String(required=True)

    @validates('action')
    def validate_action(self, value):
        return value in ['login', 'chat']


class LoginPayload(PayloadBase):
    user_id = fields.String(required=True)
    token = fields.String(required=True)

    @validates('token')
    def validate_action(self, token):
        return bool(token)


class ChatMessagePayload(PayloadBase):
    target_type = fields.String(required=True)
    target_name = fields.String(required=True)  # user or room name
    message = fields.String()


class ChallengePayload(PayloadBase):
    target_type = fields.String(required=True)  # player, room
    target_name = fields.String(required=True)  # username, room
    challenge_action = fields.String(required=True, validate=lambda m: m in ['create',
                                                                             'accept',
                                                                             'decline',
                                                                             'revise'])
    message = fields.String()
