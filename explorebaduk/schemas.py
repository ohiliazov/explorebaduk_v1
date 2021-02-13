from typing import Optional, Set

from pydantic import BaseModel, validator

from explorebaduk.constants import (
    ALLOWED_GAME_TYPES,
    ALLOWED_RULES,
    ALLOWED_TIME_SYSTEMS,
)


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


class MyFriendsOut(BaseModel):
    mutual: Set[int]
    sent: Set[int]
    received: Set[int]

    class Config:
        schema_extra = {
            "example": {
                "mutual": {132, 242, 312},
                "sent": {412, 523},
                "received": {676},
            },
        }


class GameSetup(BaseModel):
    name: str
    type: str
    is_private: bool = False

    @validator("type")
    def validate_game_type(cls, value: str):
        assert value in ALLOWED_GAME_TYPES, f"Invalid game_type: {value}"

    class Config:
        schema_extra = {
            "example": {
                "name": "My first game",
                "type": ALLOWED_GAME_TYPES[0],
                "is_private": False,
            },
        }


class RuleSet(BaseModel):
    rules: str
    board_size: int = 19

    @validator("rules")
    def validate_rules(cls, value: str):
        assert value in ALLOWED_RULES, f"Invalid rules: {value}"

    @validator("board_size")
    def validate_board_size(cls, value: int):
        assert 5 <= value <= 52, f"Invalid board_size: {value}"

    class Config:
        schema_extra = {
            "example": {
                "rules": ALLOWED_RULES[0],
                "board_size": 19,
            },
        }


class TimeSettings(BaseModel):
    time_system: str
    main_time: int = 0
    overtime: int = 0
    periods: int = 1
    stones: int = 1
    bonus: int = 0

    @validator("time_system")
    def validate_time_system(cls, value: str):
        assert value in ALLOWED_TIME_SYSTEMS, f"Invalid time_system: {value}"

    class Config:
        schema_extra = {
            "example": {
                "time_system": ALLOWED_TIME_SYSTEMS[2],
                "main_time": 3600,
                "overtime": 30,
                "periods": 5,
            },
        }


class Challenge(BaseModel):
    game_setup: GameSetup
    rule_set: RuleSet
    time_settings: TimeSettings
