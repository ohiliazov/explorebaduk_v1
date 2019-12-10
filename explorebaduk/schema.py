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


class TimeControlSchema(Schema):
    setting = fields.String(required=True)
    main = fields.Integer()
    overtime = fields.Integer()
    periods = fields.Integer()
    stones = fields.Integer()
    bonus = fields.Integer()

    @validates('setting')
    def validate_setting(self, value):
        if value not in VALID_TIME_SETTINGS:
            raise ValidationError(f"Invalid time control setting: {value}")

    @validates_schema
    def validate_time_control(self, data, **kwargs):
        if data['setting'] == ABSOLUTE and not data.get('main'):
            raise ValidationError("Absolute time control should have main time.")

        elif data['setting'] == BYOYOMI and not (data.get('overtime') and data.get('periods')):
            raise ValidationError("Byoyomi time control should have overtime and periods.")

        elif data['setting'] == CANADIAN and not (data.get('overtime') and data.get('stones')):
            raise ValidationError("Canadian time control should have overtime and stones.")

        elif data['setting'] == FISCHER and not data.get('bonus'):
            raise ValidationError("Fischer time control should have bonus time.")

    @post_load
    def set_time_control(self, data, **kwargs):
        for item in ['main', 'overtime', 'periods', 'stones', 'bonus']:
            data.setdefault(item, 0)

        if data['setting'] == NO_TIME:
            data['main'] = float('+inf')

        if data['setting'] == ABSOLUTE:
            data['overtime'] = 0
            data['periods'] = 0
            data['stones'] = 0
            data['bonus'] = 0

        elif data['setting'] == BYOYOMI:
            data['stones'] = 1
            data['bonus'] = 0

        elif data['setting'] == CANADIAN:
            data['periods'] = 1
            data['bonus'] = 0

        elif data['setting'] == FISCHER:
            data['overtime'] = 0
            data['periods'] = 0
            data['stones'] = 0

        return data


class ChallengeSchema(Schema):
    opponent_id = fields.Integer(default=None)  # in case of direct challenge
    name = fields.String()
    ruleset = fields.String(required=True)
    board_size = fields.String(required=True)
    to_join = fields.Integer(default=2)

    time_control = fields.Nested(TimeControlSchema, required=True)
    no_undo = fields.Boolean(default=False)
    no_pause = fields.Boolean(default=False)
