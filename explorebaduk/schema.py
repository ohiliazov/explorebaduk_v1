from marshmallow import Schema, fields, pre_load, post_load, validates, validates_schema, ValidationError

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


class TimeSettingsSchema(Schema):
    time_system = fields.Integer(required=True)
    main_time = fields.Integer(required=True)
    overtime = fields.Integer(required=True)
    periods = fields.Integer(required=True)
    stones = fields.Integer(required=True)
    bonus = fields.Integer(required=True)
    delay = fields.Integer(required=True)

    @validates('time_system')
    def validate_time_system(self, value):
        if value not in VALID_TIME_SETTINGS:
            raise ValidationError(f"Invalid time control setting: {value}")

    @validates_schema
    def validate_time_control(self, data, **kwargs):
        time_system = data['time_system']
        if time_system == ABSOLUTE and not data['main']:
            raise ValidationError("Absolute time control should have main time.")

        elif time_system == BYOYOMI and not (data['overtime'] and data['periods']):
            raise ValidationError("Byoyomi time control should have overtime and periods.")

        elif time_system == CANADIAN and not (data['overtime'] and data['stones']):
            raise ValidationError("Canadian time control should have overtime and stones.")

        elif time_system == FISCHER and not data['bonus']:
            raise ValidationError("Fischer time control should have bonus time.")

    @post_load
    def set_time_control(self, data, **kwargs):
        for item in ['main', 'overtime', 'periods', 'stones', 'bonus', 'delay']:
            data.setdefault(item, 0)

        if data['time_system'] == NO_TIME:
            data['main'] = float('+inf')

        if data['time_system'] == ABSOLUTE:
            data['overtime'] = 0
            data['periods'] = 0
            data['stones'] = 0
            data['bonus'] = 0

        elif data['time_system'] == BYOYOMI:
            data['stones'] = 1
            data['bonus'] = 0

        elif data['time_system'] == CANADIAN:
            data['periods'] = 1
            data['bonus'] = 0

        elif data['time_system'] == FISCHER:
            data['overtime'] = 0
            data['periods'] = 0
            data['stones'] = 0
            data['delay'] = 0

        return data


class RestrictionSchema(Schema):
    is_open = fields.Integer(required=True)
    undo = fields.Integer(required=True)
    pause = fields.Integer(required=True)


class NewChallengeSchema(Schema):
    game_type = fields.Integer(required=True)
    rules = fields.Integer(required=True)
    players = fields.Integer(required=True)
    board_width = fields.Integer(required=True)
    board_height = fields.Integer(required=True)

    restrictions = fields.Nested(RestrictionSchema, required=True)
    time_settings = fields.Nested(TimeSettingsSchema, required=True)

    @validates_schema()
    def check_board_size(self, data, **kwargs):
        height = data['board_height']
        width = data['board_width']

        if any([not (4 < int(value) < 53) for value in [height, width]]):
            raise ValidationError(f"Board size is out of range: {height}:{width}")

    @pre_load
    def convert(self, data: dict, **kwargs):
        for key, value in data.items():
            if key in self.fields:
                data[key] = int(value)

        data["restrictions"] = {key: data.pop(key) for key in RestrictionSchema().fields}
        data["time_settings"] = {key: data.pop(key) for key in TimeSettingsSchema().fields}

        return data


