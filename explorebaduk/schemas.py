from typing import Optional, Set

from pydantic import BaseModel, validator

from explorebaduk.constants import GameCategory, RuleSet, TimeSystem


class PlayerOut(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    email: str
    username: str
    rating: float = 10
    puzzle_rating: float = 0
    avatar: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "user_id": 123,
                "first_name": "John",
                "last_name": "Doe",
                "email": "johndoe@explorebaduk.com",
                "username": "johndoe",
                "rating": 1992.532,
                "puzzle_rating": 1605.321,
                "avatar": "avatar.jpg",
            },
        }


class FriendListOut(BaseModel):
    user_id: Optional[int]
    friends: Set[int]
    friends_out: Set[int]
    friends_in: Set[int]

    class Config:
        schema_extra = {
            "example": {
                "friends": {132, 242, 312},
                "friends_out": {412, 523},
                "friends_in": {676},
            },
        }


class TimeSettings(BaseModel):
    time_system: TimeSystem
    main_time: int = 0
    overtime: int = 0
    periods: int = 1
    stones: int = 1
    bonus: int = 0
    max_time: Optional[int]

    @validator("main_time", "overtime", "bonus")
    def validate_non_negative(cls, v: int):
        assert v >= 0
        return v

    @validator("periods", "stones")
    def validate_positive(cls, v: int):
        assert v > 0
        return v

    @validator("main_time")
    def validate_main_time(cls, v: int, values, **kwargs):
        if values["time_system"] == TimeSystem.ABSOLUTE:
            assert v >= 60, "main_time should be >= 60 seconds in Absolute time system"
        return v

    @validator("periods")
    def validate_periods(cls, v: int, values, **kwargs):
        if values["time_system"] != TimeSystem.BYOYOMI:
            assert v == 1, "periods can be > 1 only in Byo-Yomi time system"
        return v

    @validator("stones")
    def validate_stones(cls, v: int, values, **kwargs):
        if values["time_system"] != TimeSystem.CANADIAN:
            assert v == 1, "stones can be > 1 only in Canadian time system"
        return v

    @validator("bonus")
    def validate_bonus(cls, v: int, values, **kwargs):
        if values["time_system"] != TimeSystem.FISCHER:
            assert v == 0, "bonus can be > 0 only in Fischer time system"
        return v

    @validator("max_time")
    def validate_max_time(cls, v: int, values, **kwargs):
        if values["time_system"] != TimeSystem.FISCHER:
            assert v is None, "max_time can be set only in Fischer time system"
        return v

    class Config:
        schema_extra = {
            "example": {
                "time_system": TimeSystem.BYOYOMI,
                "main_time": 3600,
                "overtime": 30,
                "periods": 5,
                "stones": 1,
                "bonus": 0,
                "max_time": 0,
            },
        }


class OpenGame(BaseModel):
    name: str
    board_size: int = 19
    is_ranked: bool = False
    is_private: bool = False
    category: GameCategory
    rules: RuleSet
    time_settings: TimeSettings
    opponent_id: Optional[int]

    @validator("board_size")
    def validate_board_size(cls, v: int):
        assert 5 <= v <= 52, "Board size should be between 5 and 52"
        return v

    class Config:
        schema_extra = {
            "example": {
                "name": "My first game",
                "board_size": 19,
                "is_ranked": False,
                "is_private": False,
                "category": GameCategory.REAL_TIME,
                "rules": RuleSet.JAPANESE,
                "time_settings": TimeSettings.Config.schema_extra["example"],
            },
        }
