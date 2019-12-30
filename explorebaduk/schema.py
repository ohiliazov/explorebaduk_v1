from marshmallow import Schema, fields, post_load, validates, validates_schema, ValidationError

from explorebaduk.constants import (
    VALID_TIME_SETTINGS,
    NO_TIME,
    ABSOLUTE,
    BYOYOMI,
    CANADIAN,
    FISCHER,
)


class LoginSchema(Schema):
    user_id = fields.Integer(required=True)
    token = fields.String(required=True)


class RuleSetSchema(Schema):
    rules = fields.String(required=True)
    board_height = fields.Integer(required=True)
    board_width = fields.Integer()
    to_join = fields.Integer(default=2)

    @validates_schema
    def check_board_size(self, data, **kwargs):
        height = data['board_height']
        width = data.get('board_width', height)

        if any([not 5 < int(value) < 52 for value in [height, width]]):
            raise ValidationError(f"Board size is out of range: {height}:{width}")

    @post_load
    def adjust_width(self, data, **kwargs):
        data['board_width'] = data.get('board_width') or data['board_height']

        return data


class TimeSystemSchema(Schema):
    type = fields.String(required=True)
    main = fields.Integer()
    overtime = fields.Integer()
    periods = fields.Integer()
    stones = fields.Integer()
    bonus = fields.Integer()
    delay = fields.Integer()

    @validates('type')
    def validate_type(self, value):
        if value not in VALID_TIME_SETTINGS:
            raise ValidationError(f"Invalid time control setting: {value}")

    @validates_schema
    def validate_time_control(self, data, **kwargs):
        if data['type'] == ABSOLUTE and not data.get('main'):
            raise ValidationError("Absolute time control should have main time.")

        elif data['type'] == BYOYOMI and not (data.get('overtime') and data.get('periods')):
            raise ValidationError("Byoyomi time control should have overtime and periods.")

        elif data['type'] == CANADIAN and not (data.get('overtime') and data.get('stones')):
            raise ValidationError("Canadian time control should have overtime and stones.")

        elif data['type'] == FISCHER and not data.get('bonus'):
            raise ValidationError("Fischer time control should have bonus time.")

    @post_load
    def set_time_control(self, data, **kwargs):
        for item in ['main', 'overtime', 'periods', 'stones', 'bonus', 'delay']:
            data.setdefault(item, 0)

        if data['type'] == NO_TIME:
            data['main'] = float('+inf')

        if data['type'] == ABSOLUTE:
            data['overtime'] = 0
            data['periods'] = 0
            data['stones'] = 0
            data['bonus'] = 0

        elif data['type'] == BYOYOMI:
            data['stones'] = 1
            data['bonus'] = 0

        elif data['type'] == CANADIAN:
            data['periods'] = 1
            data['bonus'] = 0

        elif data['type'] == FISCHER:
            data['overtime'] = 0
            data['periods'] = 0
            data['stones'] = 0
            data['delay'] = 0

        return data


class RestrictionsSchema(Schema):
    no_undo = fields.Boolean(default=False)
    no_pause = fields.Boolean(default=False)
    no_analyze = fields.Boolean(default=False)
    is_private = fields.Boolean(default=False)


class ChallengeBaseSchema(Schema):
    rule_set = fields.Nested(RuleSetSchema, required=True)
    time_system = fields.Nested(TimeSystemSchema, required=True)
    restrictions = fields.Nested(RestrictionsSchema, required=True)


class ChallengeSchema(ChallengeBaseSchema):
    type = fields.String(required=True)
    name = fields.String(required=True)


class ChallengeJoinSchema(ChallengeBaseSchema):
    creator_id = fields.Integer()
