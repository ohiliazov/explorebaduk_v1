from marshmallow import Schema, pre_load, ValidationError


class BaseSchema(Schema):
    __pattern__ = None

    @pre_load
    def parse_message(self, message, **kwargs):
        data = self.__pattern__.match(message)

        if not data:
            raise ValidationError(message)

        return {key: value for key, value in data.groupdict().items() if value is not None}
