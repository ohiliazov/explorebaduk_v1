import re
from typing import Type, Any
from enum import Enum
from marshmallow import (
    Schema,
    fields,
    pre_load,
    post_load,
    validate,
    validates_schema,
    ValidationError,
)


from explorebaduk.constants import (
    GameType,
    Ruleset,
    TimeSystem,
    PlayerColor,
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


class BaseSchema(Schema):
    __pattern__ = None

    @pre_load
    def parse_message(self, message, **kwargs):
        data = self.__pattern__.match(message)

        if not data:
            raise ValidationError(message)

        return {key: value for key, value in data.groupdict().items() if value is not None}


class LoginSchema(BaseSchema):
    __pattern__ = re.compile(r"^(?P<token>\w{64})$")

    token = fields.String(required=True, validate=validate.Length(equal=64))


class ChallengeNewSchema(BaseSchema):
    __pattern__ = re.compile(
        r"GN\[(?P<name>[\w\W]+)\]"    # challenge name
        r"GI\["                       # game info
        r"(?P<game_type>\d+)"
        r"R(?P<rules>\d+)"
        r"W(?P<width>\d+)"
        r"H(?P<height>\d+)"
        r"(MIN(?P<rank_lower>\d+))?"  # min rank is optional
        r"(MAX(?P<rank_upper>\d+))?"  # max rank is optional
        r"\]"
        r"FL\["                       # flags
        r"(?P<is_open>\d)"
        r"(?P<undo>\d)"
        r"(?P<pause>\d)"
        r"\]"
        r"TS\["                       # time system
        r"(?P<time_system>\d+)"
        r"(M(?P<main_time>\d+))?"
        r"(O(?P<overtime>\d+))?"
        r"(P(?P<periods>\d+))?"
        r"(S(?P<stones>\d+))?"
        r"(B(?P<bonus>\d+))?"
        r"(D(?P<delay>\d+))?"
        r"\]"
    )
    name = fields.String(required=True)

    game_type = fields.Integer(required=True, validate=EnumValidator(GameType))
    rules = fields.Integer(required=True, validate=EnumValidator(Ruleset))
    width = fields.Integer(required=True, validate=validate.Range(min=5, max=52))
    height = fields.Integer(required=True, validate=validate.Range(min=5, max=52))
    rank_lower = fields.Integer(missing=0, validate=validate.Range(min=0, max=3000))
    rank_upper = fields.Integer(missing=3000, validate=validate.Range(min=0, max=3000))

    is_open = fields.Boolean(required=True)
    undo = fields.Boolean(required=True)
    pause = fields.Boolean(required=True)

    time_system = fields.Integer(required=True, validate=EnumValidator(TimeSystem))
    main_time = fields.Integer(missing=0)
    overtime = fields.Integer(missing=0)
    periods = fields.Integer(missing=0)
    stones = fields.Integer(missing=0)
    bonus = fields.Integer(missing=0)
    delay = fields.Integer(missing=0)

    @validates_schema
    def validate_time_control(self, data, **kwargs):
        time_system = TimeSystem(data["time_system"])
        if time_system is TimeSystem.ABSOLUTE and not data["main_time"] > 0:
            raise ValidationError("Absolute time control should have main time.")

        elif time_system is TimeSystem.BYOYOMI and not (data["overtime"] > 0 and data["periods"] > 0):
            raise ValidationError("Byoyomi time control should have overtime and periods.")

        elif time_system is TimeSystem.CANADIAN and not (data["overtime"] > 0 and data["stones"] > 0):
            raise ValidationError("Canadian time control should have overtime and stones.")

        elif time_system is TimeSystem.FISCHER and not data["bonus"] > 0:
            raise ValidationError("Fischer time control should have bonus time.")

    @post_load
    def convert_enums(self, data, **kwargs):
        data["game_type"] = GameType(data["game_type"])
        data["rules"] = Ruleset(data["rules"])
        data["time_system"] = TimeSystem(data["time_system"])
        return data


class ChallengeIdSchema(BaseSchema):
    __pattern__ = re.compile(r"^(?P<challenge_id>\d+)$")
    challenge_id = fields.Integer(required=True)


class ChallengeStartSchema(BaseSchema):
    __pattern__ = re.compile(r"^(?P<challenge_id>\d+) (?P<opponent_id>\d+)$")
    challenge_id = fields.Integer(required=True)
    opponent_id = fields.Integer(required=True)
