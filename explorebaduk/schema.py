from typing import Type, Any
from enum import Enum
from marshmallow import Schema, fields, pre_load, post_load, validate, validates, validates_schema, ValidationError


from explorebaduk.constants import (
    GameType,
    Ruleset,
    TimeSystem,
)


class EnumValidator(validate.Validator):
    """Validator which succeeds if the enumerator contains value.

    :param enum: The enumerator which should contain given value.
    """

    def __init__(self, enum: Type[Enum] = None):
        self.enum = enum

    def _repr_args(self) -> str:
        return "enum={!r}".format(self.enum.__name__)

    def __call__(self, value) -> Any:
        try:
            self.enum(value)
        except ValueError:
            raise ValidationError(f"'{value!r}' is not a valid {self.enum.__name__}.")

        return value


class LoginSchema(Schema):
    user_id = fields.Integer(required=True)
    token = fields.String(required=True)


class ChallengeSchema(Schema):
    challenge_id = fields.Integer()

    is_open = fields.Boolean(required=True)
    undo = fields.Boolean(required=True)
    pause = fields.Boolean(required=True)

    time_system = fields.Integer(required=True, validate=EnumValidator(TimeSystem))
    main_time = fields.Integer(required=True)
    overtime = fields.Integer(required=True)
    periods = fields.Integer(required=True)
    stones = fields.Integer(required=True)
    bonus = fields.Integer(required=True)
    delay = fields.Integer(required=True)

    @validates_schema
    def validate_time_control(self, data, **kwargs):
        time_system = TimeSystem(data["time_system"])
        if time_system is TimeSystem.ABSOLUTE and not data["main"] > 0:
            raise ValidationError("Absolute time control should have main time.")

        elif time_system is TimeSystem.BYOYOMI and not (data["overtime"] > 0 and data["periods"] > 0):
            raise ValidationError("Byoyomi time control should have overtime and periods.")

        elif time_system is TimeSystem.CANADIAN and not (data["overtime"] > 0 and data["stones"] > 0):
            raise ValidationError("Canadian time control should have overtime and stones.")

        elif time_system is TimeSystem.FISCHER and not data["bonus"] > 0:
            raise ValidationError("Fischer time control should have bonus time.")

    @post_load
    def set_time_control(self, data, **kwargs):
        time_system = TimeSystem(data["time_system"])
        data["time_system"] = time_system

        time_overrides = {
            TimeSystem.NO_TIME: {
                "main_time": float("+inf"),
                "overtime": 0,
                "periods": 0,
                "stones": 0,
                "bonus": 0,
                "delay": 0,
            },
            TimeSystem.ABSOLUTE: {"overtime": 0, "periods": 0, "stones": 0, "bonus": 0},
            TimeSystem.BYOYOMI: {"stones": 1, "bonus": 0},
            TimeSystem.CANADIAN: {"periods": 1, "bonus": 0},
            TimeSystem.FISCHER: {"overtime": 0, "periods": 0, "stones": 0},
        }
        data.update(time_overrides[time_system])

        return data


class NewChallengeSchema(ChallengeSchema):
    game_type = fields.Integer(required=True, validate=EnumValidator(GameType))
    rules = fields.Integer(required=True, validate=EnumValidator(Ruleset))
    players = fields.Integer(required=True, validate=validate.Range(min=1))
    width = fields.Integer(required=True, validate=validate.Range(min=5, max=52))
    height = fields.Integer(required=True, validate=validate.Range(min=5, max=52))
