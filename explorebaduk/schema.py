from marshmallow import Schema, fields, pre_load, post_load, validate, validates, validates_schema, ValidationError

from explorebaduk.constants import (
    GameType,
    Ruleset,
    TimeSystem,
)
from explorebaduk.models.challenge import Challenge


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
        try:
            TimeSystem(value)
        except ValueError:
            raise ValidationError(f"Invalid time control setting: {value}")

    @validates_schema
    def validate_time_control(self, data, **kwargs):
        time_system = TimeSystem(data['time_system'])
        if time_system is TimeSystem.ABSOLUTE and not data['main']:
            raise ValidationError("Absolute time control should have main time.")

        elif time_system is TimeSystem.BYOYOMI and not (data['overtime'] and data['periods']):
            raise ValidationError("Byoyomi time control should have overtime and periods.")

        elif time_system is TimeSystem.CANADIAN and not (data['overtime'] and data['stones']):
            raise ValidationError("Canadian time control should have overtime and stones.")

        elif time_system is TimeSystem.FISCHER and not data['bonus']:
            raise ValidationError("Fischer time control should have bonus time.")

    @post_load
    def set_time_control(self, data, **kwargs):
        time_system = TimeSystem(data['time_system'])

        data['time_system'] = time_system

        if time_system is TimeSystem.NO_TIME:
            data['main'] = float('+inf')

        if time_system is TimeSystem.ABSOLUTE:
            data['overtime'] = 0
            data['periods'] = 0
            data['stones'] = 0
            data['bonus'] = 0

        elif time_system is TimeSystem.BYOYOMI:
            data['stones'] = 1
            data['bonus'] = 0

        elif time_system is TimeSystem.CANADIAN:
            data['periods'] = 1
            data['bonus'] = 0

        elif time_system is TimeSystem.FISCHER:
            data['overtime'] = 0
            data['periods'] = 0
            data['stones'] = 0
            data['delay'] = 0

        return data


class RestrictionSchema(Schema):
    is_open = fields.Integer(required=True, validate=validate.Range(min=0, max=1))
    undo = fields.Integer(required=True, validate=validate.Range(min=0, max=1))
    pause = fields.Integer(required=True, validate=validate.Range(min=0, max=1))


class NewChallengeSchema(Schema):
    game_type = fields.Integer(required=True)
    rules = fields.Integer(required=True)
    players = fields.Integer(required=True, validate=validate.Range(min=1))
    width = fields.Integer(required=True, validate=validate.Range(min=5, max=52))
    height = fields.Integer(required=True, validate=validate.Range(min=5, max=52))

    restrictions = fields.Nested(RestrictionSchema, required=True)
    time_settings = fields.Nested(TimeSettingsSchema, required=True)

    @validates('game_type')
    def validate_game_type(self, value):
        try:
            GameType(value)
        except ValueError:
            raise ValidationError(f"Invalid game type: {value}")

    @validates('rules')
    def validate_rules(self, value):
        try:
            Ruleset(value)
        except ValueError:
            raise ValidationError(f"Invalid rules: {value}")

    @pre_load
    def prepare_data(self, data: dict, **kwargs):
        for key, value in data.items():
            if key in self.fields:
                data[key] = int(value)

        data["restrictions"] = {key: data.pop(key) for key in RestrictionSchema().fields}
        data["time_settings"] = {key: data.pop(key) for key in TimeSettingsSchema().fields}

        return data

    @post_load
    def prepare_object(self, data, **kwargs):
        game_type = GameType(data['game_type'])
        data['game_type'] = game_type
        data['rules'] = Ruleset(data['rules'])

        if game_type in [GameType.RANKED,
                         GameType.FREE]:
            data['players'] = 2

        elif game_type in [GameType.DEMO]:
            data['players'] = 1

        elif game_type in [GameType.RENGO]:
            data['players'] = 4

        return data
