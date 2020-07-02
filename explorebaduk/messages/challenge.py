import re
from marshmallow import (
    fields,
    post_load,
    validate,
    validates_schema,
    ValidationError,
)

from explorebaduk.constants import TimeSystem, GameRules
from explorebaduk.helpers import EnumValidator
from explorebaduk.messages.base import BaseSchema


# challenge new GN[name]SZ[5:5]TS[1M3000O30P3S1B0]
# challenge cancel 1
# challenge start 1 2
# challenge join 1
# challenge leave 1


class ChallengeIDSchema(BaseSchema):
    __pattern__ = re.compile(r"^(?P<challenge_id>\d+)$")
    challenge_id = fields.Integer(required=True)


class ChallengeNewSchema(BaseSchema):
    __pattern__ = re.compile(
        r"GN\[(?P<name>[\w\W]+)\]"  # challenge name
        r"SZ\[(?P<width>\d+):(?P<height>\d+)\]"  # board size
        r"RU\[(?P<rules>[a-z]+)\]"  # rules
        r"TS\["  # time system
        r"(?P<time_system>\d+)(?:M(?P<main_time>\d+))?"
        r"(?:O(?P<overtime>\d+))?(?:P(?P<periods>\d+))?"
        r"(?:S(?P<stones>\d+))?(?:B(?P<bonus>\d+))?"
        r"\]"
    )
    name = fields.String(required=True)

    width = fields.Integer(required=True, validate=validate.Range(min=5, max=52))
    height = fields.Integer(required=True, validate=validate.Range(min=5, max=52))

    rules = fields.String(required=True, validate=EnumValidator(GameRules))

    time_system = fields.Integer(required=True, validate=EnumValidator(TimeSystem))
    main_time = fields.Integer(missing=0)
    overtime = fields.Integer(missing=0)
    periods = fields.Integer(missing=0)
    stones = fields.Integer(missing=0)
    bonus = fields.Integer(missing=0)

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
        data["time_system"] = TimeSystem(data["time_system"])
        return data
